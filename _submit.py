from requests import session, utils
from re import compile, sub
from json import loads, dumps
from sys import platform
from os import environ
from random import uniform
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from urllib.parse import quote
from Crypto.Cipher import AES
from base64 import b64encode

class Submit(object):
	def __init__(self, name : str, longitude : str, latitude : str, address : str):
		self.__version = "1.0.6"
		if "linux" in platform:
			self.runtime_path = "/tmp/parse-runtime.log" # 运行时日志
		elif "win" in platform:
			self.runtime_path = environ["TEMP"] + "\\parse-runtime.log"
		else:
			print("Cannot find your operating system")
			quit()
		self.name = name
		self.key = "2knV5VGRTScU7pOq"
		self.iv = "UmNWaNtM0PUdtFCs"
		self.longitude = longitude # 经度
		self.latitude = latitude # 纬度
		self.address = address # 在地图上的文字信息
		self.session = session() # 请求会话
		self.year = str(datetime.now().year)
		self.month = str(datetime.now().strftime("%m"))
		self.day = str(datetime.now().strftime("%d"))
		self.date = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
		print(self.date)

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

		self.headers = {
			"User-Agent": "Mozilla/5.0 (iPhone; XT2201-2 " \
				"Build/S1SC32.52-69-24; wv) AppleWebKit/537.36 " \
				"(KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 " \
				"Mobile Safari/537.36;webank/h5face;webank/1.0 yiban_iOS/5.0.12",
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With": "com.yiban.app",
			"Origin": "https://app.uyiban.com",
			"Referer": "https://app.uyiban.com/",
			"Connection": "Close"
		}

	def task(self, cookies : dict):
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
					"CSRF": cookies["csrf_token"]
				},
				headers = self.headers,
				allow_redirects = False
			).text
		)["data"]:
			task[i["TaskId"]] = i["Title"]
		return task

	# 获取任务细节和加密任务Key
	def submit(self, name : str, taskId : str, title : str, cookies : dict):
		runtime = open(self.runtime_path, "ab+")
		errmsg = ""
		self.session.cookies = utils.cookiejar_from_dict(cookies)
		wfid = loads(
			self.session.get(
				url = "https://api.uyiban.com/officeTask/client/index/detail",
				params = {
					"TaskId": taskId,
					"CSRF": cookies["csrf_token"]
				},
				headers = self.headers,
				allow_redirects = False
			).text
		)["data"]
		processId = self.session.post(
			url = "https://api.uyiban.com/workFlow/c/my/getProcessDetail",
			params = {
				"WFId": wfid["WFId"],
				"CSRF": cookies["csrf_token"]
			},
			headers = self.headers,
			allow_redirects = False
		).text
		processId = compile("\"Id\": ?\"([0-9a-zA-Z-_]+[^\", ])\"?,?").findall(processId)[0]
		quest = loads(
			self.session.get(
				url = "https://api.uyiban.com/workFlow/c/my/form/" + wfid["WFId"],
				params = {
					"CSRF": cookies["csrf_token"]
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
					"time": self.date,
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
				"CSRF": cookies["csrf_token"]
			},
			headers = self.headers,
			data = data,
			allow_redirects = False
		).text
		if loads(submit)["code"] == 0: # 请求成功
			runtime.write(
				bytes(
					"\n====\t====\t====\n" +
					"Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
					"\nTitle: " + title +
					"\nAccount: " + name +
					"\nTaskId: " + taskId +
					"\nWFId: " + wfid["WFId"] +
					"\nProcessId: " + processId +
					"\nContent: " + wfid["Content"] +
					"\n====\t====\t====\n", encoding = "UTF-8"
				)
			)
		else: # 请求失败
			errmsg += (
				"\n====\t====\t====\n" +
				"Submit error.\nLog: " + name + "\n" +
				str(loads(submit)["code"]) + "\n" + loads(submit)["msg"] + 
				"\n====\t====\t====\n"
			)
			runtime.write(bytes(errmsg, encoding = "UTF-8"))
		print("\033[1;32mAll Done.\033[0m")
		runtime.close()
		return errmsg

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
