from hashlib import md5
from datetime import datetime
from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar
from re import compile
from json import loads
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from urllib.parse import quote, urlencode, parse_qs
from base64 import b64encode
from js2py import eval_js
from config import HEADERS

class Cookies(object):
    def __init__(self, account: str, password: str):
        self.headers = HEADERS
        self.get_cookies_count = 0
        self.session = Session()
        self.session.keep_alive = False
        self.phpsessid = None
        self.account = account
        self.password = password.encode('UTF-8')
        self.cookies = dict(errmsg = None)
        self.csrf = md5(str(datetime.now()).encode('UTF-8')).hexdigest()
        self.verify_code = None

        while self.get_cookies_count < 2:
            self.get_cookies_count += 1

            self.session.cookies = cookiejar_from_dict({
                'csrf_token': self.csrf
            })
            self.session.headers = self.headers
            self.session.headers.update(
                Referer = 'https://c.uyiban.com/',
                Origin = 'https://c.uyiban.com'
            )
            result = self.session.get(
                url = 'https://api.uyiban.com/base/c/auth/yiban',
                params = {
                    'CSRF': self.csrf
                },
                allow_redirects = False
            )
            self.phpsessid = dict_from_cookiejar(self.session.cookies)['PHPSESSID']
            result = self.session.get(
                url = loads(result.content)['data']['Data'],
                allow_redirects = True
            )
            self.page_use = compile(r'page_use ?= ?[\'|"]([a-zA-Z0-9-_]+)[\'|"]').findall(result.text)[0]
            cipher = PKCS1_v1_5.new(RSA.importKey(compile(r"id=\"key\" ?value=\"?([0-9a-zA-Z -_/=+\n]+[^\"])\"? ").findall(result.text)[0]))
            waf = dict_from_cookiejar(self.session.cookies)['https_waf_cookie']
            _YB = dict_from_cookiejar(self.session.cookies)['_YB_OPEN_V2_0']
            self.session.headers.update(
                Referer = result.url,
                Origin = 'https://oauth.yiban.cn'
            )
            result = self.session.post(
                url = 'https://oauth.yiban.cn/code/usersure',
                params = {
                    'ajax_sign': self.page_use
                },
                data = urlencode({
                    'oauth_uname': self.account,
                    'oauth_upwd': b64encode(cipher.encrypt(self.password)),
                    'client_id': '95626fa3080300ea',
                    'redirect_uri': 'https://f.yiban.cn/iapp7463',
                    'state': '',
                    'scope': '1,2,3,4,',
                    'display': 'html'
                }),
                allow_redirects = False
            )
            if 'error' in loads(result.text)['reUrl']:
                self.cookies['errmsg'] = f'{self.account}\tLogin fail.\n'
                continue
            self.session.headers.update(Referer = 'https://oauth.yiban.cn/')
            # del self.session.headers['Origin']
            result = self.session.get(
                url = loads(result.content)['reUrl'],
                allow_redirects = False
            )
            if len(result.text) > 10: # enter decryption
                a = self.ydclearance(result.text)
                b = dict_from_cookiejar(self.session.cookies)
                b['https_ydclearance'] = a[0]
                self.session.cookies = cookiejar_from_dict(b)
                self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
                result = self.session.get(
                    url = f'https://f.yiban.cn{a[1]}',
                    allow_redirects = False
                )
                waf = dict_from_cookiejar(self.session.cookies)['https_waf_cookie']
                self.headers.update(Referer = result.url)
                # del self.headers["Origin"]
            else:
                waf = dict_from_cookiejar(self.session.cookies)['https_waf_cookie']
                self.headers.update(Referer = result.url, Origin = "https://f.yiban.cn")
            result = self.session.get(
                url = result.headers['Location'],
                allow_redirects = False
            )
            self.verify_code = compile(r"verify_request=([^&]+)&?").findall(result.headers["Location"])[0]
            self.session.headers.update(
                Referer = "https://c.uyiban.com/",
                Origin = "https://c.uyiban.com"
            )
            i = 0
            result = self.session.get(
                url = 'https://api.uyiban.com/base/c/auth/yiban',
                params = {
                    "verifyRequest": self.verify_code,
                    "CSRF": self.csrf
                },
                cookies = {},
                allow_redirects = False
            )

            self.cookies = dict_from_cookiejar(self.session.cookies)
            self.cookies['account'] = self.account
            self.cookies['domain'] = 'uyiban.com'

            if self.cookies.get('errmsg') == None: break


    def __del__(self):
        self.session.close()

    def get_cookies(self) -> dict:
        return self.cookies

    def ydclearance(self, text: str) -> list:
        result = compile(r"(function ([a-z]{2,})\(.+) ?</script>").findall(text)
        js_code = str(result[0][0])
        js_code = js_code.replace(r'eval("qo=eval;qo(po);");', r"return po;")
        js_code += "\n" + result[0][1] + "(" + compile(r"window.onload=setTimeout\(\"" + result[0][1] + r"\(([0-9]+).+").findall(text)[0] + ");"
        result = eval_js(js_code)
        return [compile(r"https?_ydclearance=([0-9a-zA-Z-_]+);?").findall(result)[0], compile(r"window\.document\.location=\'(.+)\'").findall(result)[0]]



