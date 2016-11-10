SmartQQBot
=========

+ 使用文档见[User Guide](resources/UserGuide.md)
+ 二次开发[Developers Guide](resources/DevelopersGuide.md)
+ 贡献文档[Contribution Guide](resources/ContributionGuide.md)
+ API 文档[API Reference](resources/API.md)
+ 常见问题[FAQ](resources/FAQ.md)(no-gui登录, debug模式, etc)

## 依赖
+ `PIL` or `Pillow`
+ `six` and `requests`
+ `bottle` （可选）

## 快速开始
+ 安装Python \> 2.6 / Python \>= 3(tested on 3.4)
+ 手动安装依赖`pip install Pillow six requests` 或者在命令行运行`python setup.py develop`
+ 如果需要启用web界面登录，请`pip install bottle`
+ 命令行运行 `python run.py`
+ 等待弹出二维码进行扫描登陆, 或手动打开脚本所在目录的v.jpg进行扫描。
+ 控制台不再输出登录确认的log的时候就登录成功了
+ 首次登陆过后, 以后的登陆会尝试使用保存的cookie进行自动登录（失败后会自动弹出二维码进行二维码登陆）
+ 配置插件之后, 才能使用QQBot的调教功能（参见下方插件配置）

## docker 使用  
+ docker build --force-rm --rm -q -t yourtag -f Dockerfile .  
+ docker run -dit --name qq -P -v yourcookiepath:/app/src/cookie yourtag  --no-gui --http
+ docker run -dit --name qq -P -v yourcookiepath:/app/src/cookie yourtag --no-gui --http --new-user #新建用户  

**若使用上有疑惑, 欢迎加群473413233讨论**

## 特性

+ 二维码登录（支持本地扫码和浏览器扫码)
+ 插件支持, 支持原生Python Package, 支持插件热 启用/关闭
+ 群消息, 讨论组消息, 私聊消息, 通知消息接收和发送
+ 支持获取群号群名、群成员名称、真实QQ号等信息
+ 同时支持Python2/3

### 基础功能
注: 插件默认启用了basic、weather和manager, 如需其他功能请自行配置开启

+ 唤出功能(basic[callout]), 聊天内容中检测关键词`智障机器人`, 若发言中包含该词, 将自动回复`干嘛（‘·д·）`, 此功能一般用于检测机器人状态与调戏
+ 复读功能(basic[repeat]), 检测到群聊中***连续两个***回复内容相同, 将自动复读该内容1次。
+ 群聊吐槽功能(tucao), 类似于小黄鸡, 在群中通过发送以下语句实现功能:
    + **注意tucao插件默认没有开启，如需要开启以下功能请手动修改配置文件**
    + `!learn {ha}{哈哈}`语句, 则机器人检测到发言中包含“ha”时将自动回复“哈哈”。
    + `!delete {ha}{哈哈}`可以删除该内容。吐槽内容本地保存在data/tucao_save/中。
    + `!吐槽列表` 可以列出当前所有的吐槽及其对应关键字
    + `!删除关键字 {ha}` 可以删除对应关键字ha下面的所有吐槽
+ 天气查询功能(weather), 使用`天气 城市`或者`waether 城市`语句, 查询对应城市的天气消息
+ 更多插件说明请查看使用文档[User Guide](resources/UserGuide.md)

### 内置插件
+ 插件管理器
+ 基础插件（唤出、复读)
+ 图灵机器人（需要安装requests库并自行申请key）
+ Satoru（简单的吐槽机器人）
+ 天气查询插件

## 插件配置
### 如何载入插件

1. 确认插件文件已放在src\\smart\_qq\_plugins目录中
2. 如果src\\config\\目录中没有plugin.json, 手动复制plugin.json.example并改名为plugin.json
3. 打开plugin.json, 修改其中启用的插件列表plugin_on, 将需要启动的插件名称追加到列表中

注: 插件名称为你的PythonPackage或者插件文件的名字

## 已知问题
+ 由于WebQQ协议的限制, 机器人回复消息有可能会被屏蔽, 暂时还没有较好的解决方案。
+ <s>加载多个插件后, 可以接受消息, 但无法正确发送(resolved)</s>
+ <s>天气插件在Python3暂时无法正确运行，会提示“City not found”</s>

## ChangeLog
+ 2016.08.25 支持Web界面登录，查看当前登录是否过期， 重新登录
+ 2016.08.18 支持Python3

## RoadMap

+ 支持每个插件的单独配置文件

## Contributors
+ [Yinzo](https://github.com/Yinzo)
+ [Cheng Gu](https://github.com/gucheen)
+ [winkidney](https://github.com/winkidney)
+ [eastpiger](https://github.com/eastpiger)

