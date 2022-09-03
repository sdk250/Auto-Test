# 简介
这是一个易班APP的打卡API的整合仓库<br>
你可以使用 `parse.py` 来进行某些操作<br>
# 使用方法
`Clone` 该仓库或下载仓库 `parse.py` 的raw到本地<br>
使用前请确保你的工作环境具有 `Chrome Driver` 和
`pip` 的软件包: `requests` , `pycryptodome` , `json` ,
`selenium` , `base64` , `urllib` <br>
然后在您的工作目录新建 `<item>.py` <br>
并且键入<br>
```
from parse import Parse
a = Parse(account = <Your Account>, password = <Your Password>)
a.get_task() # Get quest id
a.get_WFId() # Get WFId
a.get_processid() # Get processid
a.submit() # Submit information
```
如果运行成功，程序将会在您的工作目录输入 `parse-runtime.log` 打卡日志。
如果在运行时日志 `runtime.log` 中看到错误信息，请配合 `/tmp/parse-run.log`
来查阅并解决错误。
# 