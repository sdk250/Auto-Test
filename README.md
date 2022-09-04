# 简介
这是一个易班APP的打卡API的整合仓库<br>
你可以使用 `parse.py` 来进行某些操作<br>

# 使用方法
`Clone` 该仓库或下载仓库 `parse.py` 的raw到本地。<br>
使用前请确保您的工作环境具有 `Chrome Driver` 和
`python3-pip` 的软件包: `requests` , `pycryptodome` , `json` ,
`selenium` , `base64` , `urllib` <br>
然后在您的工作目录新建 `<item>.py` <br>
并且键入: <br>
```python
from parse import Parse
a = Parse(account = <Your Account>, password = <Your Password>)
a.get_task() # Get quest id
a.get_WFId() # Get WFId
a.get_processid() # Get processid
a.submit() # Submit information
```
如果运行成功，程序将会在您的 `/tmp/parse-runtime.log` 打卡日志。<br>
如果您在运行时日志 `parse-runtime.log` 中看到错误信息，请配合 `/tmp/parse-run.log`
来查阅并解决错误。<br>

# 注意事项
使用前请修改 `parse.py` 中 `self.longitude` , `self.latitude` , `self.address` , `self.institution`
, `self.publisher` 为您本地化的 `value` <br>
默认为本人的学校和发布机构<br>

# FAQ
> - Q: 为什么要用Python写?
>> - A: 人生苦短，我用Python

> - Q: 如何安装上述提到的软件包?
>> - A: 前提需要你安装了 `Python 3.5 +` 然后输入 `pip3 install <package>`

> - Q: 支持 `Windows` 吗?
>> - A: 暂时没有时间，您可以自行修改适配 `Windows` 代码量几分钟就能完成



---
# 使用须知
---
本项目仅用于学习交流，如果您认为部分代码侵犯了您的权益，<br>
请与我联系
> Google Email: 520sdk250@gmail.com<br>
> QQ/TIM: 2094858273<br>
> Tel: 13085354260<br>
部分代码参考: [参考一](https://www.programminghunter.com/article/39181948028/) ,
[参考二](https://gitee.com/ye-qiuming/nnu_yiban)