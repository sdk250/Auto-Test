from sys import platform
from os import environ

if "linux" in platform:
	runtime_path = "/tmp/parse-runtime.log" # 运行时日志
elif "win" in platform:
	runtime_path = environ["TEMP"] + "\\parse-runtime.log"
else:
	print("Cannot find your operating system")
	quit()

ID = {
	"Account": "Password" # 多账号支持
}

global_longitude = "Your global longitude"
global_latitude = "Your global latitude"
global_address = "Your address for text"

email_server = False # 如果设置为True，则必须填写下面三项
server_email = "Send email"
server_email_key = "Send email key"
client_email = "Recv email"
