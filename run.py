from parse import Parse
a = Parse(
	account = "Zhangsan", # 易班登录账号
	password = "Lisi", # 易班登录密码
	warn = True, # 此项为可选，如果为True则必须填写 server_mail, client_mail, email_key 这三项
	server_mail = "zhangsan@123.com", # 发送方邮箱
	client_mail = "lisi@123.com", # 接收方邮箱
	email_key = "Login Token", # 发送方邮箱登录Token
	longitude = "100.123", # 可选，设定打卡时的定位的经度
	latitude = "20.321", # 可选，设定打卡时的定位的纬度
	address = "China" # 可选，设定以上经纬在地图上面文字信息
)