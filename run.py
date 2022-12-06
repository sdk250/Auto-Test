from _cookies import Cookies
# from os.path import exists
# from os import remove
# from re import compile
from datetime import datetime
from _submit import Submit
from config import ID, email_server, server_email, server_email_key, client_email, global_longitude, global_latitude, global_address, global_headers, runtime_path
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

if __name__ == "__main__":
	errmsg = "\n"
	for i in ID.keys():
		submit = Submit(headers = global_headers, runtime_path = runtime_path, name = None, longitude = global_longitude, latitude = global_latitude, address = global_address)
		try:
			_cookies = Cookies(headers = global_headers, account = i, password = ID[i])
		except:
			errmsg += i + "\tGet cookies failure.\n"
			continue
		if isinstance(_cookies.cookies, dict):
			task = submit.task(_cookies.cookies)
			if task == {}:
				errmsg += i + "\tTask is None.\n"
			for j in task.keys():
				if "每日" in task[j]:
					errmsg += submit.submit(name = i, taskId = j, title = task[j], cookies = _cookies.cookies)
				else:
					errmsg += i + "\tInvild item.\n"
		else:
			errmsg += _cookies.cookies
	if errmsg != "\n":
		print(errmsg)
		with open(runtime_path, "a+") as fd:
			fd.write(errmsg)
		if email_server:
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
		