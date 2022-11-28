from _cookies import Cookies
from os.path import exists
from os import remove
from re import compile
from datetime import datetime
from _submit import Submit
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

ID = {
	"Account": "Password" # 多账号支持
}
server_email = "Send email"
server_email_key = "Send email key"
client_email = "Recv email"

if __name__ == "__main__":
	submit = Submit(name = None, longitude = "Your longitude", latitude = "Your latitude", address = "Your address for text")
	cookies = Cookies()
	errmsg = "\n"
	for i in ID.keys():
		_cookies = cookies._cookies(account = i, password = ID[i])
		if isinstance(_cookies, dict):
			task = submit.task(_cookies)
			if task == {}:
				errmsg += i + "\tTask is None.\n"
			for j in task.keys():
				errmsg += submit.submit(name = i, taskId = j, title = task[j], cookies = cookies)
		else:
			errmsg += _cookies
	if errmsg != "\n":
		smtp_host = "smtp.qq.com" # Only supported QQ email
		smtp_port = 465 # QQ邮箱的SMTP服务端口号
		smtpObj = SMTP_SSL(smtp_host) # 初始化QQ邮箱SSL加密通道
		smtpObj.connect(smtp_host, smtp_port)
		smtpObj.login(server_email, server_email_key)
		msg = MIMEText(errmsg, "plain", "UTF-8")
		msg["From"] = Header("Server_Parse")
		msg["To"] = Header("Client")
		msg["Subject"] = Header("Error messages output!", "UTF-8")
		try:
			smtpObj.sendmail(server_email, client_email, msg.as_string())
			errmsg += str(datetime.now()) + "\tMail send success.\n"
		except:
			errmsg += str(datetime.now()) + "\tMail send failure.\n"
		smtpObj.close()
		print(errmsg)