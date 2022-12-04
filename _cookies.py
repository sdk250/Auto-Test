from hashlib import md5
from datetime import datetime
from requests import session, utils
from re import compile
from json import loads
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from urllib.parse import quote
from base64 import b64encode
from js2py import eval_js

class Cookies(object):
	def __init__(self, account : str = None, password : str = None):
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
		self.errmsg = None
		self.get_cookies_count = 0
		self.session = session()
		self.phpsessid = None
		self.csrf = None
		self.account = account
		self.password = password
		if self.account or self.password != None:
			self.cookies = self._cookies(account = self.account, password = self.password)

	def _cookies(self, account : str, password : str):
		self.get_cookies_count += 1
		if self.get_cookies_count > 10:
			self.errmsg += "\tGET COOKIES ERROR.\n"
			return self.errmsg
		self.errmsg = "\n"
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
		waf = compile("https_waf_cookie=([0-9a-zA-Z-_]+);{1}").findall(result.headers["Set-Cookie"])[0]
		_YB = compile("_YB_OPEN_V2_0=([0-9a-zA-Z-_]+);{1}").findall(result.headers["Set-Cookie"])[0]
		# _X = compile("_X=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
		# _Y = compile("_Y=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
		# _Z = compile("_Z=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
		# _C = compile("_C=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
		# _S = compile("_S=([0-9a-zA-Z]+);{1}").findall(result.headers["Set-Cookie"])[0]
		self.session.cookies = utils.cookiejar_from_dict({
			"https_waf_cookie": waf,
			"_YB_OPEN_V2_0": _YB,
			# "_X": _X,
			# "_Y": _Y,
			# "_Z": _Z,
			# "_C": _C,
			# "_S": _S
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
		if "error" in loads(result.text)["reUrl"]:
			self.errmsg += self.account + "\tLogin fail.\n"
			self._cookies(account = account, password = self.password)
			return self.errmsg
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
		self.headers.update(Referer = "https://c.uyiban.com/", Origin = "https://c.uyiban.com")
		result = self.session.get(
			url = "https://api.uyiban.com/base/c/auth/yiban",
			params = {
				"verifyRequest": verify_code,
				"CSRF": self.csrf
			},
			headers = self.headers,
			allow_redirects = False
		)
		if self.errmsg == "\n":
			return {
				"cpi": compile("cpi=([0-9a-zA-Z%]+[^;]);?").findall(result.headers["Set-Cookie"])[0],
				"PHPSESSID": self.phpsessid,
				"csrf_token": self.csrf,
				"is_certified": "1"
			}
		else:
			return self.errmsg

	def ydclearance(self, text : str):
		result = compile(r"(function ([a-z]{2,})\(.+) ?</script>").findall(text)
		js_code = str(result[0][0])
		js_code = js_code.replace(r'eval("qo=eval;qo(po);");', r"return po;")
		js_code += "\n" + result[0][1] + "(" + compile(r"window.onload=setTimeout\(\"" + result[0][1] + "\(([0-9]+).+").findall(text)[0] + ");"
		result = eval_js(js_code)
		return [compile("https?_ydclearance=([0-9a-zA-Z-_]+);?").findall(result)[0], compile("window\.document\.location=\'(.+)\'").findall(result)[0]]