from cookies import Cookies
from datetime import datetime
from submit import Submit
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import config

if __name__ == "__main__":
    print(f"Version: {config.__version}")
    for i in config.ID.keys():
        errmsg = "\n"
        _config = {}
        for j in config.keys:
            if config.ID[i].get(j) != None:
                _config[j] = config.ID[i][j]
            else:
                _config[j] = config._global[j]
        submit = Submit(
            headers = config._global["headers"],
            runtime_path = config.runtime_path,
            name = None,
            longitude = _config["longitude"],
            latitude = _config["latitude"],
            address = _config["address"],
            info = _config["info"]
        )
        cookies = Cookies(
            headers = config._global["headers"],
            account = i,
            password = config.ID[i]["passwd"]
        )
        if "errmsg" in cookies.cookies.keys():
            errmsg += f'{i}\t{cookies.cookies["errmsg"]}\n'
        else:
            task = submit.task(cookies.cookies)
            if task == {}:
                errmsg += f"{i}\tTask is None.\n"
            for j in task.keys():
                if "每日" in task[j]:
                    errmsg += submit.submit(name = i, taskId = j, title = task[j], cookies = cookies.cookies)
                else:
                    errmsg += f"{i}\tInvalid item.\n"

        del submit, cookies

        if errmsg != "\n":
            print(errmsg)

            if _config["email_server"]:
                smtp_host = "smtp.qq.com" # Only supported QQ email
                smtp_port = 465 # QQ邮箱的SMTP服务端口号
                try:
                    smtpObj = SMTP_SSL(smtp_host) # 初始化QQ邮箱SSL加密通道
                    smtpObj.connect(smtp_host, smtp_port)
                    smtpObj.ehlo(smtp_host)
                    smtpObj.login(_config["server_email"], _config["server_email_key"])
                    msg = MIMEText(errmsg, "plain", "UTF-8")
                    msg["From"] = Header(_config["server_email"])
                    msg["To"] = Header(_config["client_email"])
                    msg["Subject"] = Header("Error messages output!", "UTF-8")
                    smtpObj.sendmail(_config["server_email"], _config["client_email"], msg.as_string())
                    errmsg += f"{str(datetime.now())}\tMail send success.\n"
                except:
                    errmsg += f"{str(datetime.now())}\tMail send failure.\n"
                smtpObj.quit()
                smtpObj.close()

            with open(config.runtime_path, "a+") as fd:
                fd.write(errmsg)

