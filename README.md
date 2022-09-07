# 简介
这是一个易班APP的打卡API的整合仓库<br>
你可以使用 `parse.py` 来进行某些操作<br>
就目前而言，只支持 `Linux` 分支系统<br>

# 功能更新日志
- 2022年9月7日
> 新增打卡失败发送邮件提醒功能

# 使用方法
`Clone` 该仓库或下载仓库 `parse.py` 的raw到本地。<br>
使用前请确保您的工作环境具有 `Chrome Driver` 和
`python3-pip` 的软件包: `requests` , `pycryptodome` , `json` ,
`selenium` , `base64` , `urllib` <br>
然后在您的工作目录新建 `<item>-run.py` <br>
并且键入: <br>
```python
from parse import Parse
a = Parse(account = <Your Account>,
	password = <Your Password>,
	server_mail = <Your sender email>,
	email_key = <Sender email login token>,
	client_mail = <Receiver email>
)
~ a.get_task() # Get quest id
a.get_WFId() # Get WFId
a.get_processid() # Get processid
a.submit() # Submit information ~
a.run() #Just <Parse(obj).run()> to running
```
如果运行成功，程序将会在您的 `/tmp` 目录输出 `parse-runtime.log` 日志。<br>
如果您在运行时日志 `parse-runtime.log` 中看到错误信息，请配合 `/tmp/parse-run.log`
来查阅并解决错误。<br>

# 自动化
如果以上运行都没有发生任何错误，恭喜你接下来进入自动化阶段。<br>
目前仅提供 `Linux Branch` - `Debian` 的教程:<br>
- 首先安装Crontab
```shell
$> sudo apt install cronie -y
```
- 然后输入<br>
```shell
$> crontab -e
```
- 继续输入<br>
```shell
30 8,12,20 * * * /usr/bin/python3 <Your work directory>/<item>-run.py
```
以上含义为每天早8，中12，晚8点半各执行一次打卡<br>
我的学校是这样来的，请按照您的本地化进行修改<br>
就此，自动化结束。<br>

# 注意事项
使用前请修改 `parse.py` 中 `self.longitude` , `self.latitude` , `self.address` , ~`self.institution`
, `self.publisher`~ (以上两项已设定为自动获取，无需手动输入) 为您本地化的 `value` <br>
默认为本人的学校和发布机构<br>

# FAQ
> Q: 为什么要用Python写?
>> - A: 人生苦短，我用Python

> Q: 如何安装上述提到的软件包?
>> - A: 前提需要你安装了 `Python 3.5 +` 然后输入 `pip3 install <package>`

> Q: 支持 `Windows` 吗?
>> - A: 暂时没有时间，您可以自行修改适配 `Windows` 代码量几分钟就能完成

> Q: 为什么不在 `parse.py` 中写注释?
>> - A: 抱歉，因为我实在没时间，后面一定加上

> Q: Why not use English?
>> - A: I think no one use it except Chinese student.

> Q: 作者是昆明冶金的吗?
>> - A: 是的，所以我的项目中大部分的设定都是围绕着我们学校来的

> Q: 作者学号?
>> - A: 首先，我很能理解你想 `感谢` 我的心情。所以 你的好意我心领了

---
# 使用须知
---
本项目仅用于学习交流，如果您认为部分代码侵犯了您的权益，<br>
请与我联系
> Google Email: 520sdk250@gmail.com<br>
> QQ/TIM: 2094858273<br>
> Tel: +86 13085354260<br>
部分代码参考: [参考一](https://www.programminghunter.com/article/39181948028/) ,
[参考二](https://gitee.com/ye-qiuming/nnu_yiban)