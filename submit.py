from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
from re import compile, sub
from json import loads, dumps
from os import path
from random import uniform
from datetime import datetime, timedelta
from urllib.parse import quote
from Crypto.Cipher import AES
from base64 import b64encode
from config import HEADERS, PATH

class Submit(object):
    def __init__(self, cookies: dict, session = None):
        self.headers = HEADERS
        self.key = "2knV5VGRTScU7pOq"
        self.iv = "UmNWaNtM0PUdtFCs"
        self.cookies = cookies
        self.external_session = False
        self.session = None
        if session == None:
            self.external_session = True
            self.session = Session() # 请求会话
            self.session.cookies = cookiejar_from_dict(self.cookies)
            self.session.keep_alive = False
            self.session.headers = self.headers
        else:
            self.external_session = False
            self.session = session
        self.date = str(datetime.now().strftime('%Y-%m-%d %H:%M'))

    def __del__(self):
        if not self.external_session:
            self.session.close()

    def get(self) -> dict:
        task = dict()
        self.session.headers['Origin'] = 'https://app.uyiban.com'
        self.session.headers['Referer'] = 'https://app.uyiban.com/'
        result = loads(
            self.session.get(
                url = 'https://api.uyiban.com/officeTask/client/index/uncompletedList',
                params = {
                    'StartTime': datetime.strftime(
                        datetime.now() - timedelta(days = 20),
                        '%Y-%m-%d %H:%M'
                    ),
                    'EndTime': datetime.strftime(
                        datetime.now() + timedelta(days = 5),
                        '%Y-%m-%d %H:%M'
                    ),
                    'CSRF': self.cookies['csrf_token']
                },
                allow_redirects = False
            ).content
        )
        if result['code'] != 0: return dict(errmsg = result['msg'])
        for i in result["data"]: task[i["TaskId"]] = i["Title"]
        return task

    def get_wfid(self, taskId: str) -> dict:
        return loads(
            self.session.get(
                url = "https://api.uyiban.com/officeTask/client/index/detail",
                params = {
                    'TaskId': taskId,
                    'CSRF': dict_from_cookiejar(self.session.cookies)['csrf_token']
                },
                allow_redirects = False
            ).content
        )

    def get_processid(self, wfid: str) -> str:
        processId = self.session.post(
            url = "https://api.uyiban.com/workFlow/c/my/getProcessDetail",
            params = {
                "WFId": wfid,
                "CSRF": self.cookies['csrf_token']
            },
            allow_redirects = False
        ).text
        return compile(r'"Id": ?"([0-9a-zA-Z-_]+[^", ])"?,?').findall(processId)[0]

    def get_task(self, wfid) -> dict:
        return loads(
            self.session.get(
                url = f'https://api.uyiban.com/workFlow/c/my/form/{wfid}',
                params = {
                    "CSRF": self.cookies["csrf_token"]
                },
                allow_redirects = False
            ).content
        )['data']['Form']

    # 获取任务细节和加密任务Key
    def submit(self,
        name: str,
        wfid: dict,
        quest: dict,
        processId: str,
        taskId: str,
        title: str,
        longitude: float,
        latitude: float,
        address: str,
        returnSchool: str,
        lock: any
    ) -> str:
        errmsg = ''
        data = "Str=" + self.encrypt_data({
            "WFId": wfid['WFId'],
            "Data": dumps({
                quest[1]["id"]: returnSchool,
                quest[2]["id"]: str(round((36 + uniform(0, 0.9)), 1)),
                quest[3]["id"]: ['以上都无'],
                quest[4]["id"]: '好',
                quest[5]["id"]: {
                    "time": self.date,
                    "longitude": str(longitude),
                    "latitude": str(latitude),
                    "address": address
                }
            }, ensure_ascii = False),
            "WfprocessId": processId,
            "Extend": dumps({
                "TaskId": taskId,
                "title": "任务信息",
                "content":[
                    {
                        "label": "任务名称",
                        "value": title
                    }, {
                        "label": "发布机构",
                        "value": wfid["PubOrgName"]
                    }, {
                        "label": "发布人",
                        "value": wfid["PubPersonName"]
                    }
                ]
            }, ensure_ascii = False),
            "CustomProcess": dumps({
                "ApplyPersonIds": [],
                "CCPersonId": []
            }, ensure_ascii = False)
        }, self.key, self.iv)
        self.headers["Content-Length"] = str(len(data))
        submit = self.session.post(
            url = "https://api.uyiban.com/workFlow/c/my/apply",
            params = {
                "CSRF": self.cookies["csrf_token"]
            },
            headers = self.headers,
            data = data,
            allow_redirects = False
        ).text
        if loads(submit)["code"] == 0: # 请求成功
            lock.acquire()
            with open(path.join(PATH, 'run.log'), 'a+') as f:
                f.write(
                    "\n====\t====\t====\n" +
                    "Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                    "\nTitle: " + title +
                    "\nAccount: " + name +
                    "\nTaskId: " + taskId +
                    "\nWFId: " + wfid["WFId"] +
                    "\nProcessId: " + processId +
                    "\nContent: " + wfid["Content"] +
                    "\n====\t====\t====\n"
                )
            lock.release()
        else: # 请求失败
            errmsg += (
                "\n====\t====\t====\n" +
                "Submit error.\nLog: " + name + "\n" +
                str(loads(submit)["code"]) + "\n" + loads(submit)["msg"] +
                "\n====\t====\t====\n"
            )
        print(f'{name}\t\033[1;32mDone.\033[0m')
        return errmsg

    def encrypt_data(self, data: str, key: str, iv: str) -> str:
        data = dumps(data, ensure_ascii = False).replace(" ", "")
        res = sub(compile(r'(\d{4}-\d+-\d{2,}:\d{2,})'), str(self.date), data)
        res = res + (
            AES.block_size - len(res.encode()) % AES.block_size
        ) * chr(
            AES.block_size - len(res.encode()) % AES.block_size
        )
        cipher = AES.new(
            key.encode("UTF-8"),
            AES.MODE_CBC,
            iv.encode("UTF-8")
        )
        result = b64encode(
            b64encode(
                cipher.encrypt(res.encode("UTF-8"))
            )
        )
        return quote(result.decode("UTF-8"))




