SmartQQ-for-Raspberry-Pi(PiWebQQV2)
=========

基于 [SmartQQ](http://w.qq.com/) 编写, 登陆时采用QQ安全中心的二维码做为登陆条件, 不需要在程序里输入QQ号码及QQ密码.

关于自动获取 QRCode 图片的方法: 我采用方法是让程序将图片保存到自己的Web站点下,然后自己通过Web方式访问得到QRCode, 然后用手机扫描.

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
