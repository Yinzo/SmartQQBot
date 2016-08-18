SmartQQBot
=========

+ 使用文档见[User Guide](resources/UserGuide.md)
+ 二次开发[Developers Guide](resources/DevelopersGuide.md)
+ 贡献文档[Contribution Guide](resources/ContributionGuide.md)
+ API 文档[API Reference](resources/API.md)
+ 常见问题[FAQ](resources/FAQ.md)

## 依赖
+ `PIL` or `Pillow`
+ `six` and `requests`

## 快速开始
+ 安装Python \> 2.6 / Python \>= 3(tested on 3.4)
+ 安装依赖（`pip install Pillow`或者在命令行运行python setup.py develop）
+ 命令行运行 `python run.py`
+ 等待弹出二维码进行扫描登陆, 或手动打开脚本所在目录的v.jpg进行扫描。
+ 控制台不在输出登录确认的log的时候就登录成功了
+ 首次登陆过后, 以后的登陆会尝试使用保存的cookie进行自动登录（失败后会一直loop）
+ 配置插件之后, 才能使用QQBot的调教功能（参见下方插件配置）

**若使用上有疑惑, 欢迎加群473413233讨论**

## 特性

+ 二维码登录
+ 插件支持, 支持原生Python Package, 支持插件热 启用/关闭
+ 群消息, 私聊消息, 通知消息接收和发送

### 基础功能
注: 插件默认只启用了basic、satoru和manager, 如需其他功能请自行开启

+ 唤出功能(callout), 聊天内容中检测关键词`智障机器人`, 若发言中包含该词, 将自动回复`干嘛（‘·д·）`, 此功能一般用于检测机器人状态与调戏
+ 复读功能(repeat), 检测到群聊中***连续两个***回复内容相同, 将自动复读该内容1次。
+ 群聊吐槽功能(tucao), 类似于小黄鸡, 在群中通过发送以下语句实现功能:
    + `!learn {ha}{哈哈}`语句, 则机器人检测到发言中包含“ha”时将自动回复“哈哈”。
    + `!delete {ha}{哈哈}`可以删除该内容。吐槽内容本地保存在data/tucao_save/中。
    + `!吐槽列表` 可以列出当前所有的吐槽及其对应关键字
    + `!删除关键字 {ha}` 可以删除对应关键字ha下面的所有吐槽
+ 天气查询功能(weather), 使用`天气 城市`或者`waether 城市`语句, 查询对应城市的天气消息

### 内置插件
+ 插件管理器
+ 基础插件（唤出、复读)
+ 图灵机器人（需要安装requests库）
+ Satoru（简单的吐槽机器人）
+ 天气查询插件

## 插件配置
### 如何载入插件

1. 将插件放置到smart\_qq\_plugins目录下
2. 复制plugin.json.example为plugin.json
3. 修改启用的插件列表plugin_on

注: 插件名称为你的PythonPackage或者插件文件的名字

## 已知问题
+ 由于WebQQ协议的限制, 机器人回复消息有可能会被屏蔽, 暂时还没有较好的解决方案。
+ <s>加载多个插件后, 可以接受消息, 但无法正确发送(resolved)</s>
+ 天气插件在Python3暂时无法正确运行，会提示“City not found”

## ChangeLog
+ 2016.8.18 支持Python3

## RoadMap

+ 支持每个插件的单独配置文件

## Contributors
+ [Yinzo](https://github.com/Yinzo)
+ [Cheng Gu](https://github.com/gucheen)
+ [winkidney](https://github.com/winkidney)
+ [eastpiger](https://github.com/eastpiger)

