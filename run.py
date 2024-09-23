from cookies import Cookies
from datetime import datetime
from submit import Submit
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from threading import Thread, Lock
from os import path
from time import sleep
from base64 import b64decode, b64encode
from json import loads, dumps
from sqlite3 import connect
from urllib.parse import quote, unquote
import config

def update_cookies(cookies: dict) -> None:
    with connect('config.db') as db:
        cursor = db.cursor()
        cursor.execute(
            'UPDATE Info SET Cookies = ? WHERE Account = ?;',
            (b64encode(dumps(cookies).encode('UTF-8')), cookies['account'])
        )
        cursor.close()
        db.commit()

def process(account: str,
    password: str,
    _cookies: bytes,
    longitude: float,
    latitude: float,
    address: str,
    returnSchool: str,
    email_server: bool,
    server_email: str,
    email_key: str,
    client_email: str,
    lock: Lock
) -> None:
    errmsg = ''
    invalid_cookies = False
    cookies_obj = cookies = None
    if not _cookies or \
        loads(
            b64decode(
                unquote(
                    loads(b64decode(_cookies))['cpi']
                )
            )
        )['Expire'] < int(datetime.now().timestamp()):
        invalid_cookies = True
        cookies_obj = Cookies(account, password)
        cookies = cookies_obj.cookies
        print("Cookies expired")
    else:
        cookies = loads(b64decode(_cookies))
    submit = None

    if not _cookies and cookies.get('errmsg') != None:
        errmsg += cookies['errmsg']
    else:
        if invalid_cookies:
            update_cookies(cookies)
        submit = Submit(cookies, cookies_obj.session if cookies_obj else None)
        task = submit.get()
        if task.get('errmsg') != None:
            del cookies_obj
            del submit
            del task
            cookies_obj = Cookies(account, password)
            cookies = cookies_obj.cookies
            update_cookies(cookies)
            submit = Submit(cookies, cookies_obj.session if cookies_obj else None)
            task = submit.get()

        for i,j in task.items():
            if '每日' not in j:
                continue
            wfid = submit.get_wfid(i)
            if wfid['code'] != 0:
                wfid = submit.get_wfid(i)
            processid = submit.get_processid(wfid['data']['WFId'])
            task_detail = submit.get_task(wfid['data']['WFId'])
            errmsg += submit.submit(
                account,
                wfid['data'],
                task_detail,
                processid,
                i,
                j,
                longitude,
                latitude,
                address,
                returnSchool,
                lock
            )


    if errmsg != '':
        print(errmsg)

        if email_server:
            smtp_host = "smtp.qq.com" # Only supported QQ email
            smtp_port = 465 # QQ邮箱的SMTP服务端口号
            try:
                smtpObj = SMTP_SSL(smtp_host) # 初始化QQ邮箱SSL加密通道
                smtpObj.connect(smtp_host, smtp_port)
                smtpObj.ehlo(smtp_host)
                smtpObj.login(server_email, email_key)
                msg = MIMEText(errmsg, "plain", "UTF-8")
                msg["From"] = Header(server_email)
                msg["To"] = Header(client_email)
                msg["Subject"] = Header("Error messages output!", "UTF-8")
                smtpObj.sendmail(server_email, client_email, msg.as_string())
                errmsg += f"\t{str(datetime.now())}\tMail send success.\n"
            except:
                errmsg += f"\t{str(datetime.now())}\tMail send failure.\n"
            smtpObj.quit()
            smtpObj.close()

        lock.acquire()
        with open(path.join(config.PATH, 'err.log'), "a+") as fd:
            fd.write(errmsg)
        lock.release()

if __name__ == "__main__":
    print(f"Version: {config.VERSION}")

    threads = list()
    lock = Lock()
    for i in config.ID:
        # Account,Password,Cookies,Longitude,Latitude,Address,Inschool,Email,Email_server,Server_key,Email_client,Lock
        threads.append(Thread(
            target = process,
            args = (i[0],
                i[1],
                i[2],
                config.GLOBAL['longitude'] if i[3] == None else i[3],
                config.GLOBAL['latitude'] if i[4] == None else i[4],
                config.GLOBAL['address'] if i[5] == None else i[5],
                config.GLOBAL['returnSchool'] if i[6] == None else i[6],
                config.GLOBAL['email'] if i[7] == None else i[7],
                config.GLOBAL['server_email'] if i[8] == None else i[8],
                config.GLOBAL['email_key'] if i[9] == None else i[9],
                config.GLOBAL['client_email'] if i[10] == None else i[10],
                lock
            )
        ))

    thread_count = 8
    started_threads = list()
    for i in range(len(threads) // thread_count):
        for j in range(thread_count):
            thread = threads.pop()
            thread.start()
            started_threads.append(thread)

        for j in range(len(started_threads)):
            thread = started_threads.pop()
            thread.join()

    for i in range(len(threads)):
        thread = threads.pop()
        thread.start()
        started_threads.append(thread)

    for i in started_threads:
        i.join()
