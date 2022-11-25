from _cookies import Cookies
from os.path import exists
from os import remove
from re import compile
from _submit import Submit

ID = {
	"Account": "Password" # 多账号支持
}

if __name__ == "__main__":
	for i in ID.keys():
		cookies = {}
		_name = i + ".cookies"
		submit = Submit(name = _name)
		if exists(_name):
			fd = open(_name, "r")
			for i in fd.readlines():
				i = compile("^([a-zA-Z0-9-_]+[^= ]) ?={1} ?([0-9a-zA-Z-_%]+[^\n '\"])").findall(i)[0]
				cookies[i[0]] = i[1]
			try:
				task = submit.task(cookies = cookies)
			except:
				remove(_name)
			for i in task.keys():
				submit.submit(taskId = i, title = task[i], cookies = cookies)
			fd.close()
		else:
			cookies = Cookies(account = i, password = ID[i])
			if isinstance(cookies.cookies, dict):
				fd = open(_name, "w")
				fd.write(
					"PHPSESSID = " + cookies.cookies["PHPSESSID"] +
					"\ncsrf_token = " + cookies.cookies["csrf_token"] +
					"\ncpi = " + cookies.cookies["cpi"]
				)
				task = submit.task(cookies = cookies.cookies)
				for i in task.keys():
					submit.submit(taskId = i, title = task[i], cookies = cookies.cookies)
				fd.close()
			else:
				print("Error: ", cookies.cookies)
