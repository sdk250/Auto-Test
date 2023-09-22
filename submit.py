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
    def __init__(self, headers: dict, runtime_path: str, name: str, longitude: str, latitude: str, address: str, info: dict):
        self.runtime_path = runtime_path
        self.name = name
        self.key = "2knV5VGRTScU7pOq"
        self.iv = "UmNWaNtM0PUdtFCs"
        self.longitude = longitude # 经度
        self.latitude = latitude # 纬度
        self.address = address # 在地图上的文字信息
        self.info = info
        self.session = session() # 请求会话
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().strftime("%m"))
        self.day = str(datetime.now().strftime("%d"))
        self.date = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        print(self.date)

        # 月份进制的逻辑判断，防止一些没必要的BUG
        self._year = int(self.year)
        if int(self.day) < 10:
            self._month = int(self.month) - 1
            if self._month == 0:
                self._month = 12
                self._year = int(self.year) - 1
            self._day = 30 + (int(self.day) - 10)
        else:
            self._year = int(self.year)
            self._month = int(self.month)
            self._day = int(self.day) - 10

        self.headers = headers

    def __del__(self):
        self.session.close()

    def task(self, cookies: dict) -> dict:
        self.session.cookies = utils.cookiejar_from_dict(cookies)
        task = {}
        for i in loads(
            self.session.get(
                url = "https://api.uyiban.com/officeTask/client/index/uncompletedList",
                params = {
                    "StartTime": str(self._year) + "-" + str(self._month) +
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
    def submit(self, name: str, taskId: str, title: str, cookies: dict) -> str:
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
                quest[1]["id"]: self.info["returnSchool"],
                quest[2]["id"]: self.info["temperature"],
                quest[3]["id"]: self.info["state"],
                quest[4]["id"]: self.info["mood"],
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
        del self.headers["Content-Length"]
        return errmsg

    def encrypto_data(self, data: str, key: str, iv: str) -> str:
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
