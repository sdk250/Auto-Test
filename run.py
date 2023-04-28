import config
from _cookies import Cookies
from datetime import datetime
from _submit import Submit
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

__version = "1.0.7"

if __name__ == "__main__":
	print(f"Version: {__version}")
	for i in config.ID.keys():
		errmsg = "\n"
		_config = {}
		for j in config.keys:
			try:
				_config[j] = config.ID[i][j]
			except Exception as err:
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
		try:
			_cookies = Cookies(
				headers = config._global["headers"],
				account = i,
				password = config.ID[i]["passwd"]
			)
		except:
			errmsg += f"{i}\tGet cookies failure.\n"
			continue
		if "errmsg" in _cookies.cookies:
			errmsg += f"""{i}\t{_cookies.cookies["errmsg"]}"""
		else:
			task = submit.task(_cookies.cookies)
			if task == {}:
				errmsg += f"{i}\tTask is None.\n"
			for j in task.keys():
				if "每日" in task[j]:
					errmsg += submit.submit(name = i, taskId = j, title = task[j], cookies = _cookies.cookies)
				else:
					errmsg += f"{i}\tInvalid item.\n"

		if errmsg != "\n":
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
				smtpObj.close()
			print(errmsg)
			with open(config.runtime_path, "a+") as fd:
				fd.write(errmsg)
