import config
from _cookies import Cookies
# from os.path import exists
# from os import remove
# from re import compile
from datetime import datetime
from _submit import Submit
# from config import ID, email_server, server_email, server_email_key, client_email, global_longitude, global_latitude, global_address, global_headers, info, runtime_path
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

def set_val(obj : dict, des : str):
	if des in obj.keys():
		val = obj[des]
	else:
		val = config.global_longitude
if __name__ == "__main__":
	errmsg = "\n"
	for i in config.ID.keys():
		if "longitude" in config.ID[i].keys():
			longitude = config.ID[i]["longitude"]
		else:
			longitude = config.global_longitude
		if "latitude" in config.ID[i].keys():
			latitude = config.ID[i]["latitude"]
		else:
			latitude = config.global_latitude
		if "address" in config.ID[i].keys():
			address = config.ID[i]["address"]
		else:
			address = config.global_address
		if "info" in config.ID[i].keys():
			info = config.ID[i]["info"]
		else:
			info = config.global_info
		if "email_server" in config.ID[i].keys():
			email_server = config.ID[i]["email_server"]
		else:
			email_server = config.global_email_server
		if "server_email" in config.ID[i].keys():
			server_email = config.ID[i]["server_email"]
		else:
			server_email = config.global_server_email
		if "server_email_key" in config.ID[i].keys():
			server_email_key = config.ID[i]["server_email_key"]
		else:
			server_email_key = config.global_server_email_key
		if "client_email" in config.ID[i].keys():
			client_email = config.ID[i]["client_email"]
		else:
			client_email = config.global_client_email
		submit = Submit(headers = config.global_headers, runtime_path = config.runtime_path, name = None, longitude = longitude, latitude = latitude, address = address, info = info)
		try:
			_cookies = Cookies(headers = config.global_headers, account = i, password = config.ID[i]["passwd"])
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
			with open(config.runtime_path, "a+") as fd:
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
