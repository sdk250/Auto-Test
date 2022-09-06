import time
import json
import requests
import datetime
import random
import base64
import re
import smtplib
from urllib.parse import quote
from Crypto.Cipher import AES
from selenium import webdriver
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText
from email.header import Header

class Parse(object):
	def __init__(self, **args):
		self.log_path = "/tmp/parse-run.log"
		self.TaskId = None
		self.WFId = None
		self.ProcessId = None
		self.Title = None
		self.token = None
		self.quest = None
		self.key = "2knV5VGRTScU7pOq"
		self.iv = "UmNWaNtM0PUdtFCs"
		self.institution = None
		self.publisher = None
		self.longitude = "102.442694"
		self.latitude = "24.882945"
		self.address = "云南省昆明市安宁市098乡道靠近昆明冶金高等专科学校"
		self.get_cookies_count = 0
		self.account = args["account"]
		self.password = args["password"]
		self.errmsg = "\n"
		self.server_mail = args["server_mail"]
		self.server_key = args["email_key"]
		self.client_mail = args["client_mail"]
		self.smtp_host = "smtp.qq.com"
		self.smtp_port = 465

		self.runtime = open("/tmp/parse-runtime.log", "ab+")
		self.session = requests.session()
		self.year = str(datetime.datetime.now().year)
		self.month = str(datetime.datetime.now().strftime("%m"))
		self.day = str(datetime.datetime.now().strftime("%d"))
		if int(self.day) < 10:
			self._month = int(self.month) - 1
			if self._month == 1:
				self._month = 12
				self.year = int(self.year) - 1
			self._day = 30 + (int(self.day) - 10)
		else:
			self._day = int(self.day) - 10

		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		print(str(self.date))
		self.user_agent = "Mozilla/5.0 " \
			"(iPhone; CPU iPhone OS 14_7_1 like Mac OS X) " \
			"AppleWebKit/605.1.15 (KHTML, 'like Gecko) " \
			"Mobile/15E148 yiban_iOS/5.0"
		self.headers = {
			"User-Agent": self.user_agent,
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With": "com.yiban.app",
			"Origin": "https://app.uyiban.com",
			"Referer": "https://app.uyiban.com/",
			"Connection": "Close"
		}
		self.cookies = None

		self.opt = webdriver.ChromeOptions()

		self.opt.add_argument("--headless")
		self.opt.add_argument("--disable-gpu")
		self.opt.add_argument("user-agent=" + self.user_agent)
		# opt.add_argument("--no-sandbox")

		self.get_cookies()

	def get_cookies(self):
		self.get_cookies_count += 1
		if self.get_cookies_count > 10:
			print("\033[1;31m严重错误\033[0m")
			self.runtime.write(
				bytes(
					"\n====\t====\t====\n" +
					"Date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
					"\nTitle: 出现了严重错误" +
					"\nAccount: " + self.account +
					"\n====\t====\t====\n", encoding = "UTF-8"
				)
			)
			self._quit()
		self.driver = webdriver.Chrome(
			options = self.opt,
			service_log_path = self.log_path
		)
		self.driver.get(
			"https://oauth.yiban.cn/code/html?" \
			"client_id=95626fa3080300ea&" \
			"redirect_uri=https://f.yiban.cn/iapp7463"
		)

		self.uname = self.driver.find_element(
			by = By.ID,
			value = "oauth_uname_w"
		)
		self.upwd = self.driver.find_element(
			by = By.ID,
			value = "oauth_upwd_w"
		)
		self.login = self.driver.find_element(
			by = By.CSS_SELECTOR,
			value = "button.oauth_check_login"
		)

		self.uname.send_keys(self.account)
		self.upwd.send_keys(self.password)
		self.login.click()

		time.sleep(6)

		self.set_cookies(
			self.driver.get_cookie("PHPSESSID"),
			self.driver.get_cookie("csrf_token"),
			self.driver.get_cookie("cpi")
		)

	def set_cookies(self, phpsessid, token, cpi):
		if phpsessid is None:
			print("\033[1;31mPHPSESSID is empty.\033[0m")
			self.driver.quit()
			self.get_cookies()
			return False
		elif token is None:
			print("\033[1;31mCSRF_TOKEN is empty.\033[0m")
			self.driver.quit()
			self.get_cookies()
			return False
		elif cpi is None:
			print("\033[1;31mCPI is empty.\033[0m")
			self.driver.quit()
			self.get_cookies()
			return False
		self.token = token["value"]
		self.cookies = {
			"is_certified": "1",
			"csrf_token": token["value"],
			"PHPSESSID": phpsessid["value"],
			"cpi": cpi["value"]
		}
		return self.cookies

	def get_task(self):
		self.task = self.session.get(
			url = "https://api.uyiban.com/officeTask/client/index/uncompletedList",
			params = {
				"StartTime": str(self.year) + "-" + str(self._month) +
					"-" + str(self._day) + " 00:00",
				"EndTime": self.year + "-" + self.month +
					"-" + self.day + " 23:59",
				"CSRF": self.token
			},
			headers = self.headers,
			cookies = self.cookies,
			allow_redirects = False
		)
		for i in json.loads(self.task.text)["data"]:
			if len(i) / 8 > 1:
				print("\033[1;32mMore....\033[0m")
				break;
			self.TaskId = i["TaskId"]
			self.Title = i["Title"]
		return self.task

	def get_WFId(self):
		if self.TaskId is not None:
			self.wfid = self.session.get(
				url = "https://api.uyiban.com/officeTask/client/index/detail",
				params = {
					"TaskId": self.TaskId,
					"CSRF": self.token
				},
				headers = self.headers,
				cookies = self.cookies,
				allow_redirects = False
			)
			self.WFId = json.loads(self.wfid.text)["data"]["WFId"]
			self.institution = json.loads(self.wfid.text)["data"]["PubOrgName"]
			self.publisher = json.loads(self.wfid.text)["data"]["PubPersonName"]
			return self.wfid
		else:
			print("TaskId is empty.")
			self.errmsg += "TaskId is empty.\n"
			return False

	def get_processid(self):
		if self.WFId is not None:
			self.processid = self.session.post(
				url = "https://api.uyiban.com/workFlow/c/my/getProcessDetail",
				params = {
					"WFId": self.WFId,
					"CSRF": self.token
				},
				headers = self.headers,
				cookies = self.cookies,
				allow_redirects = False
			)
			self.ProcessId = json.loads(self.processid.text)["data"]["list"][0]["Id"]
			self.quest_id = self.session.get(
				url = "https://api.uyiban.com/workFlow/c/my/form/" + self.WFId,
				params = {
					"CSRF": self.token
				},
				headers = self.headers,
				cookies = self.cookies,
				allow_redirects = False
			)
			self.quest = json.loads(self.quest_id.text)
			return {
				"processid": self.processid,
				"quest": self.quest
			}
		else:
			print("WFId is empty.")
			self.errmsg += "WFId is empty.\n"
			return False

	def submit(self):
		if self.ProcessId and self.quest and self.institution and self.publisher is not None:
			data = {
				"WFId": self.WFId,
				"Data": json.dumps({
					self.quest["data"]["Form"][1]["id"]: "是",
					self.quest["data"]["Form"][2]["id"]: str(round((36 + random.uniform(0, 1)), 1)),
					self.quest["data"]["Form"][3]["id"]: ["以上都无"],
					self.quest["data"]["Form"][4]["id"]: "好",
					self.quest["data"]["Form"][5]["id"]: {
						"time": str(self.date),
						"longitude": self.longitude,
						"latitude": self.latitude,
						"address": self.address
					}
				}, ensure_ascii = False),
				"WfprocessId": self.ProcessId,
				"Extend": json.dumps({
					"TaskId": self.TaskId,
					"title":"任务信息",
					"content":[
						{
							"label": "任务名称",
							"value": self.Title
						},
						{
							"label": "发布机构",
							"value": self.institution
						},
						{
							"label": "发布人",
							"value": self.publisher
						}
					]
				}, ensure_ascii = False),
				"CustomProcess": json.dumps({
					"ApplyPersonIds": [],
					"CCPersonId": []
				}, ensure_ascii = False)
			}
			data_ = "Str=" + self.encrypto_data(data, self.key, self.iv)
			self.submit_ = self.session.post(
				url = "https://api.uyiban.com/workFlow/c/my/apply",
				params = {
					"CSRF": self.token
				},
				headers = {
					"User-Agent": self.user_agent,
					"Content-Type": "application/x-www-form-urlencoded",
					"Content-Length": str(len(data_) + 3),
					"X-Requested-With": "com.yiban.app",
					"Origin": "https://app.uyiban.com",
					"Referer": "https://app.uyiban.com/",
					"Connection": "Close"
				},
				cookies = self.cookies,
				data = data_,
				allow_redirects = False
			)
			if json.loads(self.submit_.text)["code"] == 0:
				self.runtime.write(
					bytes(
						"\n====\t====\t====\n" +
						"Date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
						"\nTitle: " + self.Title +
						"\nAccount: " + self.account +
						"\nTaskId: " + self.TaskId +
						"\nWFId: " + self.WFId +
						"\nProcessId: " + self.ProcessId +
						"\nContent: " + json.loads(self.wfid.text)["data"]["Content"] +
						"\n====\t====\t====\n", encoding = "UTF-8"
					)
				)
			else:
				self.errmsg += "Submit error.\n"
				self.runtime.write(
					bytes(
						"\n====\t====\t====\n" +
						"Log: " + self.submit_.text +
						"\n====\t====\t====\n", encoding = "UTF-8"
					)
				)
			self._quit()
			return self.submit_
		else:
			print("Process is empty.")
			self.errmsg += "ProcessId or quest or institution or publisher is empty\n"
			return False

	def _quit(self):
		if self.errmsg != "\n":
			self.errmsg += ("Account: " + self.account)
			self.msg = MIMEText(self.errmsg, "plain", "UTF-8")
			self.msg["From"] = Header("Server_Parse")
			self.msg["To"] = Header("Client")
			self.msg["Subject"] = Header("Error messages output!", "UTF-8")
			try:
				self.smtpObj = smtplib.SMTP_SSL(self.smtp_host)
				self.smtpObj.connect(self.smtp_host, self.smtp_port)
				self.smtpObj.login(self.server_mail, self.server_key)
				self.smtpObj.sendmail(self.server_mail, self.client_mail, self.msg.as_string())
				self.msg += "Mail send success.\n"
			except:
				self.msg += "Mail send fail.\n"
			self.runtime.write(bytes(self.errmsg, encoding = "UTF-8"))
		self.driver.quit()
		self.runtime.close()
		quit()
		print("\033[1;32mAll Done.\033[0m")

	def encrypto_data(self, data, key, iv):
		_data = json.dumps(data, ensure_ascii = False).replace(" ", "")
		res = re.sub(re.compile("(\d{4}-\d+-\d{2,}:\d{2,})"), str(self.date), _data)
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
		result = base64.b64encode(
			base64.b64encode(
				cipher.encrypt(res.encode("UTF-8"))
			)
		)
		return quote(result.decode("UTF-8"))


