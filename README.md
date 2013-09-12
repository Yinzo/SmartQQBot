PiWebQQV2
=========

基于 [SmartQQ](http://w.qq.com/) 编写, 登陆时采用QQ安全中心的二维码做为登陆条件, 不需要在程序里输入QQ号码及QQ密码.

关于自动获取 QRCode 图片的方法: 我采用方法是让程序将图片保存到自己的Web站点下,然后自己通过Web方式访问得到QRCode, 然后用手机扫描.

在Pi上通过SSH后台运行的例子:
```
sudo nohup python WebQQ.py /data/http/v.jpg &
```
上面的命令在启动WebQQ之后会将`QRCode`保存到 `/data/http/v.jpg` 这个位置,然后用[QQ安全中心](http://aq.qq.com/cn2/manage/mbtoken/app_index) 扫描这个`QRCode`完成登陆.

V2版的好处在于不需要在程序里设置QQ号码和密码,在Pi所登陆的账号及密码由[QQ安全中心](http://aq.qq.com/cn2/manage/mbtoken/app_index)中指定,而且登陆时也不再需要验证码了.
`QRCode` 文件在登陆成功之后会被自动删除掉,以确保安全.
