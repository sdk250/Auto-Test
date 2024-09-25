# 简介
这是一个易班APP的打卡API的整合仓库<br>
本项目中的所有 `API` 仅对易班的 `校本化` 内的 `每日健康地址打卡` 做了表单提交的适配<br>
其他不一样的可以自行修改 `_submit.py` ，不过 `_cookies.py`应该是通用的<br>
~你可以使用 `parse.py` 来进行某些操作~<br>
就目前而言，~只支持 `Linux` 分支系统~ <br>
新增Windows支持<br>
重写架构，现在运行速度相比以前提高2倍或更多!<br>
再次重写，现在运行速度相比以前提高10倍不止！（取决于你的CPU核心）<br>

# 功能更新日志
- 2022年9月7日
> 新增打卡失败发送邮件提醒功能 (仅支持QQ邮箱)
- 2022年10月10日
> 增加Windows系统支持
- 2022年11月20日
> 重新架构，去除了对Chromium的依赖。旧的 `parse.py` 将不会再更新
- 2023年04月03日
> 优化逻辑，整体代码更加紧凑
- 2024年09月23日
> 重写架构，现在程序使用多线程的方式运行，极大的提高了运行速度。账号信息采用数据库 `sqlite3` 记录，可以更方便的管理

# 使用方法
`Clone` 该仓库或下载仓库 [releases](https://github.com/sdk250/Auto-Test/releases) 到本地。<br>
使用前请确保您的工作环境具有
`python3-pip` 的软件包: `requests` , `pycryptodome` , `json` ,
`js2py` , `base64` , `urllib` <br>
然后使用 `sqlite3` 命令操作数据库 `config.db`: <br>
```shell
sqlite3 config.db
```
比如插入一条数据：<br>
```sql
INSERT INTO Info (Account, Password) VALUES ('账号', '密码');
- 你也可以更详细地插入一条数据：
INSERT INTO Info (Account, Password, Longitude, Latitude, Address, Inschool, Email, Email_server, Server_key, Email_client) VALUES ('账号', '密码', 经度(例：100.123456), 维度(例：20.654321), '地址的文字表达', 是否返校(例：true), 邮件服务(例：false), '发件人', '发件人密钥', '收件人');
```
当未指定其中的某个字段时，使用的值为全局配置（ `config.py` ）。
配置完成以后即可直接运行：
```python
python3 run.py
```
如果运行成功，程序将会在您的当前目录输出 `run.log` （正常）或 `err.log` （错误）日志。<br>

# 自动化
如果以上运行都没有发生任何错误，恭喜你接下来进入自动化阶段。<br>
目前仅提供 `Linux Branch` - `Debian` 的教程:<br>
- 首先安装Crontab
```shell
sudo apt install cronie -y
```
- 然后输入<br>
```shell
crontab -e
```
- 继续输入<br>
```shell
30 8,12,20 * * * /usr/bin/python3 <Your work directory>/run.py
```
以上含义为每天早8，中12，晚8点半各执行一次打卡<br>
我的学校是这样来的，请按照您的本地化进行修改<br>
至此，自动化结束。<br>

# 注意事项
使用前请修改 `config.py` 中 `GLOBAL` 字典的 `longitude` , `latitude` , `address` , `returnSchool` , `email` 字段。<br>

---
# 使用须知
---
本项目仅用于学习交流，如果您认为部分代码侵犯了您的权益，<br>
请与我联系
> Google Email: 520sdk250@gmail.com<br>
部分代码参考: <br>
[参考一](https://www.programminghunter.com/article/39181948028/) <br>
[参考二](https://gitee.com/ye-qiuming/nnu_yiban)
