from hashlib import md5
from datetime import datetime
from requests import session
from requests.utils import cookiejar_from_dict
from re import compile
from json import loads
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from urllib.parse import quote
from base64 import b64encode
from js2py import eval_js

class Cookies(object):
    def __init__(self, headers: dict, account: str = None, password: str = None):
        self.headers = headers
        self.errmsg = "\n"
        self.get_cookies_count = 0
        self.session = session()
        self.phpsessid = None
        self.csrf = None
        self.account = account
        self.password = password
        if self.account and self.password != None:
            self.cookies = self._cookies(account = self.account, password = self.password)
            while self.cookies.get("errmsg") != None:
                if self.get_cookies_count < 1:
                    self.get_cookies_count += 1
                    self.cookies = self._cookies(account = self.account, password = self.password)
                else:
                    break

    def __del__(self):
        self.session.close()

    def _cookies(self, account: str, password: str) -> dict:
        self.csrf = md5(str(datetime.now()).encode("UTF-8")).hexdigest()
        self.session.cookies = cookiejar_from_dict({
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
        self.phpsessid = compile(r"PHPSESSID=([0-9a-zA-Z-]+);?").findall(result.headers["Set-Cookie"])[0]
        result = self.session.get(
            url = loads(result.text)["data"]["Data"],
            headers = self.headers,
            allow_redirects = True
        )
        self.page_use = compile(r"page_use ?= ?'([a-zA-Z0-9-_]+)'").findall(result.text)[0]
        cipher = PKCS1_v1_5.new(RSA.importKey(compile(r"id=\"key\" ?value=\"?([0-9a-zA-Z -_/=+\n]+[^\"])\"? ").findall(result.text)[0]))
        waf = compile(r"https_waf_cookie=([0-9a-zA-Z-_]+);{1}").findall(result.headers["Set-Cookie"])[0]
        _YB = compile(r"_YB_OPEN_V2_0=([0-9a-zA-Z-_]+);{1}").findall(result.headers["Set-Cookie"])[0]
        # _X = compile("_X=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
        # _Y = compile("_Y=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
        # _Z = compile("_Z=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
        # _C = compile("_C=([0-9]+);{1}").findall(result.headers["Set-Cookie"])[0]
        # _S = compile("_S=([0-9a-zA-Z]+);{1}").findall(result.headers["Set-Cookie"])[0]
        self.session.cookies = cookiejar_from_dict({
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
            params = {
                'ajax_sign': self.page_use
            },
            headers = self.headers,
            data = f"oauth_uname={account}"
                f"&oauth_upwd={password}"
                f"&client_id=95626fa3080300ea"
                f"&redirect_uri=https%3A%2F%2Ff.yiban.cn%2Fiapp7463"
                f"&state="
                f"&scope=1%2C2%2C3%2C4%2C"
                f"&display=html",
            allow_redirects = False
        )
        self.session.cookies = cookiejar_from_dict({
            "_YB_OPEN_V2_0": _YB
        })
        print(result.content)
        if "error" in loads(result.text)["reUrl"]:
            self.errmsg += f"\n{account}\tLogin fail.\n"
            return dict(errmsg = self.errmsg)
        self.headers.update(Referer = "https://oauth.yiban.cn/")
        del self.headers["Origin"]
        result = self.session.get(
            url = loads(result.text)["reUrl"],
            headers = self.headers,
            allow_redirects = False
        )
        if len(result.text) > 10: # enter decryption
            a = self.ydclearance(result.text)
            self.session.cookies = cookiejar_from_dict({
                "_YB_OPEN_V2_0": _YB,
                "https_ydclearance": a[0]
            })
            self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
            result = self.session.get(
                url = "https://f.yiban.cn" + a[1],
                headers = self.headers,
                allow_redirects = False
            )
            waf = compile(r"https_waf_cookie=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
            self.session.cookies = cookiejar_from_dict({
                "_YB_OPEN_V2_0": _YB,
                "https_waf_cookie": waf,
                "https_ydclearance": a[0]
            })
            self.headers.update(Referer = result.url)
            del self.headers["Origin"]
            result = self.session.get(
                url = result.headers["Location"],
                headers = self.headers,
                allow_redirects = False
            )
        else:
            waf = compile(r"https_waf_cookie=([0-9a-zA-Z-]+);{1}").findall(result.headers["Set-Cookie"])[0]
            self.session.cookies = cookiejar_from_dict({
                "_YB_OPEN_V2_0": _YB,
                "https_waf_cookie": waf
            })
            self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
            result = self.session.get(
                url = result.headers["Location"],
                headers = self.headers,
                allow_redirects = False
            )
        verify_code = compile(r"verify_request=([0-9a-zA-Z]+[^&])&?").findall(result.headers["Location"])[0]
        self.session.cookies = cookiejar_from_dict({
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
        i = 0
        while "Set-Cookie" not in result.headers.keys():
            if i < 5:
                i += 1
                result = self.session.get(
                    url = "https://api.uyiban.com/base/c/auth/yiban",
                    params = {
                        "verifyRequest": verify_code,
                        "CSRF": self.csrf
                    },
                    headers = self.headers,
                    allow_redirects = False
                )
            else:
                self.errmsg += f"\n{account}\tNO COOKIES RETURN\n"
                break
        if self.errmsg == "\n":
            return {
                "cpi": compile(r"cpi=([0-9a-zA-Z%]+[^;]);?").findall(result.headers["Set-Cookie"])[0],
                "PHPSESSID": self.phpsessid,
                "csrf_token": self.csrf,
                "is_certified": "1"
            }
        else:
            return dict(errmsg = self.errmsg)

    def ydclearance(self, text: str) -> list:
        result = compile(r"(function ([a-z]{2,})\(.+) ?</script>").findall(text)
        js_code = str(result[0][0])
        js_code = js_code.replace(r'eval("qo=eval;qo(po);");', r"return po;")
        js_code += "\n" + result[0][1] + "(" + compile(r"window.onload=setTimeout\(\"" + result[0][1] + r"\(([0-9]+).+").findall(text)[0] + ");"
        result = eval_js(js_code)
        return [compile(r"https?_ydclearance=([0-9a-zA-Z-_]+);?").findall(result)[0], compile(r"window\.document\.location=\'(.+)\'").findall(result)[0]]



