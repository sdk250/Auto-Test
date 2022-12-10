from sys import platform
from os import environ
from random import uniform

if "linux" in platform:
	runtime_path = "/tmp/parse-runtime.log" # 运行时日志
elif "win" in platform:
	runtime_path = environ["TEMP"] + "\\parse-runtime.log"
else:
	print("Cannot find your operating system")
	quit()

ID = {
	"Account": {
		"longitude": "Your longitude",
		"latitude": "Your latitude",
		"address": "Your address for text",
		"info": {
			"returnSchool": "是",
			"temperature": str(round((36 + uniform(0, 0.9)), 1)),
			"state": ["以上都无"],
			"mood": "好"
		},
		"email_server": False, # 如果设置为True，则必须填写下面三项
		# "server_email": "Send email",
		# "server_email_key": "Send email key",
		"client_email": "Recv email",
		# 取消注释则优先使用
		"passwd": "Password" # 多账号支持
	},
	"Account2": {
		"longitude": "Your longitude2",
		"latitude": "Your latitude2",
		"address": "Your address for text2",
		"info": {
			"returnSchool": "是",
			"temperature": str(round((36 + uniform(0, 0.9)), 1)),
			"state": ["以上都无"],
			"mood": "好"
		},
		"email_server": False, # 如果设置为True，则必须填写下面三项
		"server_email": "Send email",
		# "server_email_key": "Send email key",
		"client_email": "Recv email2",
		# 取消注释则优先使用
		"passwd": "Password2" # 多账号支持
	}
}

global_longitude = "Your global longitude"
global_latitude = "Your global latitude"
global_address = "Your address for text"

global_info = {
	"returnSchool": "是", # 是否返校
	"temperature": str(round((36 + uniform(0, 0.9)), 1)), # 随机体温值
	"state": ["以上都无"], # 您当前的状态
	"mood": "好" # 心情如何
}

global_headers = {
	"User-Agent": "Mozilla/5.0 (iPhone; XT2201-2 " \
		"Build/S1SC32.52-69-24; wv) AppleWebKit/537.36 " \
		"(KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 " \
		"Mobile Safarh5/1.0 yiban_iOS/5.0.12",
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"X-Requested-With": "com.yiban.app",
	"Origin": "https://app.uyiban.com",
	"Referer": "https://app.uyiban.com/",
	"Connection": "Close"
}

global_email_server = False # 如果设置为True，则必须填写下面三项
global_server_email = "GLOBAL Send email"
global_server_email_key = "GLOBAL Send email key"
global_client_email = "GLOBAL Recv email"
