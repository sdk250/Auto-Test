from os import environ
from urllib.parse import quote
from Crypto.Cipher import AES
from requests import session, utils
from random import uniform
from datetime import datetime
from json import loads, dumps
from hashlib import md5
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64encode
from smtplib import SMTP_SSL
from js2py import eval_js
from re import compile, sub
from email.mime.text import MIMEText
from email.header import Header
from sys import platform

class Parse(object):
	def __init__(self, account : str, password : str, email_server : bool = False,
		longitude : str = "102.442694", latitude : str = "24.882945",
		address : str = "云南省昆明市安宁市098乡道靠近昆明冶金高等专科学校", **args
	):
		self.__version = "1.0.6"
		if "linux" in platform:
			self.runtime_path = "/tmp/parse-runtime.log" # 运行时日志
		elif "win" in platform:
			self.runtime_path = environ["TEMP"] + "\\parse-runtime.log"
		else:
			print("Cannot find your operating system")
			quit()
		self.Task = {} # 未完成任务ID
		self.WFId = None
		self.csrf = None # Cookies的访问token
		self.phpsessid = None # 会话ID
		self.key = "2knV5VGRTScU7pOq"
		self.iv = "UmNWaNtM0PUdtFCs"
		self.longitude = longitude # 经度
		self.latitude = latitude # 纬度
		self.address = address # 在地图上的文字信息
		self.get_cookies_count = 0 # 获取cookies的总次数
		self.account = account
		self.password = password
		self.errmsg = "\n" # 初始错误信息

		if email_server:
			self.email_server = email_server
			self.server_email = args["server_email"] # 发送方邮箱
			self.server_key = args["server_email_key"] # 发送方邮箱登录密钥
			self.client_email = args["client_email"] # 接受方邮箱
			self.smtp_host = "smtp.qq.com" # 仅支持QQ邮箱
			self.smtp_port = 465 # QQ邮箱的SMTP服务端口号
			self.smtpObj = SMTP_SSL(self.smtp_host) # 初始化QQ邮箱SSL加密通道
			self.smtpObj.connect(self.smtp_host, self.smtp_port)
			self.smtpObj.login(self.server_email, self.server_key)
		else:
			self.email_server = False

		self.runtime = open(self.runtime_path, "ab+")
		self.session = session() # 请求会话
		self.year = str(datetime.now().year)
		self.month = str(datetime.now().strftime("%m"))
		self.day = str(datetime.now().strftime("%d"))

		# 月份进制的逻辑判断，防止一些没必要的BUG
		if int(self.day) < 10:
			self._month = int(self.month) - 1
			if self._month == 0:
				self._month = 12
				self.year = int(self.year) - 1
			self._day = 30 + (int(self.day) - 10)
		else:
			self._month = int(self.month)
			self._day = int(self.day) - 10

		self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
		print(str(self.date))
		self.user_agent = "Mozilla/5.0 (iPhone; XT2201-2 " \
			"Build/S1SC32.52-69-24; wv) AppleWebKit/537.36 " \
			"(KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 " \
			"Mobile Safari/537.36;webank/h5face;webank/1.0 yiban_iOS/5.0.12"
		self.headers = {
			"User-Agent": self.user_agent,
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With": "com.yiban.app",
			"Origin": "https://app.uyiban.com",
			"Referer": "https://app.uyiban.com/",
			"Connection": "Close"
		}

	def _cookies(self, account : str, password : str):
		self.get_cookies_count += 1
		if self.get_cookies_count > 10:
			self.errmsg += "\nGET COOKIES ERROR.\n"
			return
		self.csrf = md5(str(datetime.now()).encode("UTF-8")).hexdigest()
		self.session.cookies = utils.cookiejar_from_dict({
			"csrf_token": self.csrf
		})
		self.headers.update(Referer = "https://c.uyiban.com/", Origin = "https://c.uyiban.com")
		result = self.session.get(
			url = "https://api.uyiban.com/base/c/auth/yiban",
			params = {
				"CSRF": self.csrf
			},
			headers = self.headers,
			allow_redirects = False
		)
		self.phpsessid = compile("PHPSESSID=([0-9a-zA-Z-]+);?").findall(result.headers["Set-Cookie"])[0]
		result = self.session.get(
			url = loads(result.text)["data"]["Data"],
			headers = self.headers,
			allow_redirects = True
		)
		cipher = PKCS1_v1_5.new(RSA.importKey(compile("id=\"key\" ?value=\"?([0-9a-zA-Z -_/=+\n]+[^\"])\"? ").findall(result.text)[0]))
		try:
			waf = compile("https_waf_cookie=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_YB = compile("_YB_OPEN_V2_0=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_X = compile("_X=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_Y = compile("_Y=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_Z = compile("_Z=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_C = compile("_C=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
			_S = compile("_S=([0-9a-zA-Z]+);{1}").findall(result.headers["Set-Cookie"])[0]
		except:
			self.cookies = self._cookies(account, password)
			return
		self.session.cookies = utils.cookiejar_from_dict({
			"https_waf_cookie": waf,
			"_YB_OPEN_V2_0": _YB,
			"_X": _X,
			"_Y": _Y,
			"_Z": _Z,
			"_C": _C,
			"_S": _S
		})
		password = quote(b64encode(cipher.encrypt(bytes(password, encoding = "UTF-8"))))
		self.headers.update(Referer = result.url, Origin = "https://oauth.yiban.cn")
		result = self.session.post(
			url = "https://oauth.yiban.cn/code/usersure",
			headers = self.headers,
			data = "oauth_uname=" + account + "&oauth_upwd=" +
				password +
				"&client_id=95626fa3080300ea&redirect_uri=https%3A%2F%2Ff.yiban.cn%2Fiapp7463&state=&scope=1%2C2%2C3%2C4%2C&display=html",
			allow_redirects = False
		)
		self.session.cookies = utils.cookiejar_from_dict({
			"_YB_OPEN_V2_0": _YB
		})
		self.headers.update(Referer = "https://oauth.yiban.cn/")
		del self.headers["Origin"]
		result = self.session.get(
			url = loads(result.text)["reUrl"],
			headers = self.headers,
			allow_redirects = False
		)
		if len(result.text) > 10:
			a = self.ydclearance(result.text)
			https_ydclearance = a[0]
			self.session.cookies = utils.cookiejar_from_dict({
				"_YB_OPEN_V2_0": _YB,
				"https_ydclearance": https_ydclearance
			})
			self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
			result = self.session.get(
				url = "https://f.yiban.cn" + a[1],
				headers = self.headers,
				allow_redirects = False
			)
			waf = compile("https_waf_cookie=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
			self.session.cookies = utils.cookiejar_from_dict({
				"_YB_OPEN_V2_0": _YB,
				"https_waf_cookie": waf,
				"https_ydclearance": https_ydclearance
			})
			self.headers.update(Referer = result.url)
			del self.headers["Origin"]
			result = self.session.get(
				url = result.headers["Location"],
				headers = self.headers,
				allow_redirects = False
			)
		else:
			waf = compile("https_waf_cookie=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
			self.session.cookies = utils.cookiejar_from_dict({
				"_YB_OPEN_V2_0": _YB,
				"https_waf_cookie": waf
			})
			self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
			result = self.session.get(
				url = result.headers["Location"],
				headers = self.headers,
				allow_redirects = False
			)
		verify_code = compile("verify_request=([0-9a-zA-Z]+[^&])&?").findall(result.headers["Location"])[0]
		self.session.cookies = utils.cookiejar_from_dict({
			"csrf_token": self.csrf,
			"PHPSESSID": self.phpsessid
		})
		self.headers.update(Referer = "https://c.uyiban.com")
		result = self.session.get(
			url = "https://api.uyiban.com/base/c/auth/yiban",
			params = {
				"verifyRequest": verify_code,
				"CSRF": self.csrf
			},
			headers = self.headers,
			allow_redirects = False
		)
		cpi = compile("cpi=([0-9a-zA-Z%]+[^;]);?").findall(result.headers["Set-Cookie"])[0]
		return {
			"cpi": cpi,
			"PHPSESSID": self.phpsessid,
			"csrf_token": self.csrf,
			"is_certified": "1"
		}

	def ydclearance(self, text : str):
		result = compile(r"(function ([a-z]{2,})\(.+) ?</script>").findall(text)
		num = compile(r"window.onload=setTimeout\(\"" + result[0][1] + "\(([0-9]+).+").findall(text)
		js_code = str(result[0][0])
		js_code = js_code.replace(r'eval("qo=eval;qo(po);");', r"return po;")
		js_code += "\n" + result[0][1] + "(" + num[0] + ");"
		result = eval_js(js_code)
		return [compile("https?_ydclearance=([0-9a-zA-Z-_]+);?").findall(result)[0], compile("window\.document\.location=\'(.+)\'").findall(result)[0]]

	# 获取未完成任务ID
	def get_task(self, csrf : str, cookies : dict):
		self.session.cookies = utils.cookiejar_from_dict(cookies)
		task = {}
		for i in loads(
			self.session.get(
				url = "https://api.uyiban.com/officeTask/client/index/uncompletedList",
				params = {
					"StartTime": str(self.year) + "-" + str(self._month) +
						"-" + str(self._day) + " 00:00",
					"EndTime": self.year + "-" + self.month +
						"-" + self.day + " 23:59",
					"CSRF": csrf
				},
				headers = self.headers,
				allow_redirects = False
			).text
		)["data"]:
			task[i["TaskId"]] = i["Title"]
		return task

	# 获取任务细节和加密任务Key
	def submit(self, taskId : str, title : str, csrf : str, cookies : dict):
		self.session.cookies = utils.cookiejar_from_dict(cookies)
		wfid = loads(
			self.session.get(
				url = "https://api.uyiban.com/officeTask/client/index/detail",
				params = {
					"TaskId": taskId,
					"CSRF": csrf
				},
				headers = self.headers,
				allow_redirects = False
			).text
		)["data"]
		processId = self.session.post(
			url = "https://api.uyiban.com/workFlow/c/my/getProcessDetail",
			params = {
				"WFId": wfid["WFId"],
				"CSRF": csrf
			},
			headers = self.headers,
			allow_redirects = False
		).text
		processId = compile("\"Id\": ?\"([0-9a-zA-Z-_]+[^\", ])\"?,?").findall(processId)[0]
		quest = loads(
			self.session.get(
				url = "https://api.uyiban.com/workFlow/c/my/form/" + wfid["WFId"],
				params = {
					"CSRF": csrf
				},
				headers = self.headers,
				allow_redirects = False
			).text
		)["data"]["Form"]
		data = "Str=" + self.encrypto_data({
			"WFId": wfid["WFId"],
			"Data": dumps({
				quest[1]["id"]: "是",
				quest[2]["id"]: str(round((36 + uniform(0, 1)), 1)), # 随机体温值 (36.0 ~ 36.9)
				quest[3]["id"]: ["以上都无"],
				quest[4]["id"]: "好",
				quest[5]["id"]: {
					"time": str(self.date),
					"longitude": self.longitude,
					"latitude": self.latitude,
					"address": self.address
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
					},
					{
						"label": "发布机构",
						"value": wfid["PubOrgName"]
					},
					{
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
		self.headers.update(Referer = "https://app.uyiban.com/", Origin = "https://app.uyiban.com")
		self.headers["Content-Length"] = str(len(data))
		submit = self.session.post(
			url = "https://api.uyiban.com/workFlow/c/my/apply",
			params = {
				"CSRF": csrf
			},
			headers = self.headers,
			data = data,
			allow_redirects = False
		).text
		if loads(submit)["code"] == 0: # 请求成功
			self.runtime.write(
				bytes(
					"\n====\t====\t====\n" +
					"Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
					"\nTitle: " + title +
					"\nAccount: " + self.account +
					"\nTaskId: " + taskId +
					"\nWFId: " + wfid["WFId"] +
					"\nProcessId: " + processId +
					"\nContent: " + wfid["Content"] +
					"\n====\t====\t====\n", encoding = "UTF-8"
				)
			)
		else: # 请求失败
			self.errmsg += ("\n====\t====\t====\nSubmit error.\nLog: " + self.account + "\n" + submit + "\n====\t====\t====\n")
		self._quit()

	# 模拟析构函数，释放内存
	def _quit(self):
		if self.errmsg != "\n":
			self.errmsg += ("Account: " + self.account + "\n")
			if self.email_server == True:
				self.msg = MIMEText(self.errmsg, "plain", "UTF-8")
				self.msg["From"] = Header("Server_Parse")
				self.msg["To"] = Header("Client")
				self.msg["Subject"] = Header("Error messages output!", "UTF-8")
				try:
					self.smtpObj.sendmail(self.server_email, self.client_email, self.msg.as_string())
					self.errmsg += str(datetime.now()) + "Mail send success.\n"
				except:
					self.errmsg += str(datetime.now()) + "Mail send failure.\n"
			self.smtpObj.quit()
			self.runtime.write(bytes(self.errmsg + "\n====\t====\t====\n", encoding = "UTF-8"))
		# self.runtime.close()
		print("\033[1;32mAll Done.\033[0m")

	# 一键运行
	def run(self):
		print("Version:", self.__version)
		self.cookies = self._cookies(account = self.account, password = self.password)
		task = self.get_task(csrf = self.csrf, cookies = self.cookies)
		for i in task.keys():
			self.submit(taskId = i, title = task[i], csrf = self.csrf, cookies = self.cookies)

	# 加密表单内容
	def encrypto_data(self, data, key, iv):
		data = dumps(data, ensure_ascii = False).replace(" ", "")
		res = sub(compile("(\d{4}-\d+-\d{2,}:\d{2,})"), str(self.date), data)
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
