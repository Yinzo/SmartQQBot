SmartQQ-Bot 
=========
***该分支使用登陆部分逻辑与代码参考了[原名：SmartQQ-for-Raspberry-Pi(PiWebQQV2)](https://github.com/xqin/SmartQQ-for-Raspberry-Pi)这一项目***，以此为基础制作了基于SmartQQ的自动机器人。

登陆时采用QQ安全中心的二维码做为登陆条件, 不需要在程序里输入QQ号码及QQ密码。

##如何使用
+ ```python QQBot.py```
+ 等待提示“登陆二维码下载成功，请扫描”，打开脚本所在目录的v.jpg图片扫描二维码。
+ 等待登陆成功的提示
+ 登陆成功后出现">>"表示可输入命令，此时私聊问答功能自动激活，群聊各功能需要手动关注该群才会激活，关注群的命令为```group 群号```，此命令为控制台命令，不是在qq中发送。

##功能
<small>注：以下命令皆是在qq中发送，群聊命令发送到所在群中</small>

+ 群聊学习功能，类似于小黄鸡，在群中通过发送```!learn {ha}{哈哈}```语句，则机器人检测到发言中包含“ha”时将自动回复“哈哈”。```!delete {ha}{哈哈}```可以删除该内容。学习内容会自动储存在```groupReplys```目录中群号.save文件

+ 群聊复读功能，检测到群聊中***连续两个***回复内容相同，将自动复读该内容1次。

+ 群聊关注功能，使用命令```!follow qq号```可以使机器人复读此人所有发言（除命令外）使用命令```!unfollow qq号```解除关注。qq号处可使用"me"来快速关注与解除关注自己，例：```!follow me```

+ 私聊问答功能，可以自定义机器人私聊时提出问题，并可储存对方的回复，一般用于自动问卷调查。


##原README
在Pi上通过SSH后台运行的例子:
```
sudo nohup python WebQQ.py /data/http/v.jpg &
```
上面的命令在启动WebQQ之后会将`QRCode`保存到 `/data/http/v.jpg` 这个位置,然后用[QQ安全中心](http://aq.qq.com/cn2/manage/mbtoken/app_index) 扫描这个`QRCode`完成登陆.

例子2:
```
sudo nohup python WebQQ.py /data/http/v.jpg 48080163 &
```
上面的命令执行后的效果与第一个例子中的不同之处在于, 启动后的WebQQ只对`48080163`这个QQ号发送过来的消息做响应,其他的会忽略掉.
这样做的好处在于, 如果你的QRCode被别人扫描了,那么WebQQ就会登陆别人的QQ,然后别人就可以控制你的Pi了, 但如果加了第二个参数`48080163`,
则就算登陆了别人的QQ, 但消息的发送者并不是`48080163`, 所以发送的指令并不会被Pi所执行,从而保证安全性.
如果省略掉第2个参数,则所有人给登陆到Pi上的这个QQ发送的消息都会被解析并执行.

V2版的好处在于不需要在程序里设置QQ号码和密码,在Pi所登陆的账号及密码由[QQ安全中心](http://aq.qq.com/cn2/manage/mbtoken/app_index)中指定,而且登陆时也不再需要验证码了.
`QRCode` 文件在登陆成功之后会被自动删除掉,以确保安全.


如需使用QQ号码和密码的方式登陆可以尝试V1版本.
地址: [PiWebQQ](https://github.com/xqin/PiWebQQ)


