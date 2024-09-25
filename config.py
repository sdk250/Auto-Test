from os.path import dirname, join
from sqlite3 import connect

PATH = dirname(__file__)
VERSION = '2.0.0'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; ' \
        '(KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 ' \
        'Mobile Safarh5/1.0 yiban_iOS/5.0.12',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'com.yiban.app',
    'Origin': 'https://app.uyiban.com',
    'Referer': 'https://app.uyiban.com/',
    'Connection': 'Close'
}

ID = None

with connect(join(PATH, 'config.db')) as db:
    cursor = db.cursor()
    cursor.execute(
        'SELECT Account,Password,Cookies,Longitude,' \
        'Latitude,Address,Inschool,Email,Email_server,' \
        'Server_key,Email_client FROM Info;')
    ID = cursor.fetchall()
    cursor.close()

GLOBAL = dict(
    longitude = 100.123456,
    latitude = 20.654321,
    address = 'Your address for text.',
    returnSchool = '是', # 是否返校
    email = False, # 如果设置为True，则必须填写下面三项
    server_email = '',
    email_key = '',
    client_email = ''
)



