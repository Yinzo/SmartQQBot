QBot
=========

使用文档见[User Guide](resources/UserGuide.md)
二次开发[Developers Guide](resources/DevelopersGuide.md)
API 文档[API Reference](resources/API.md)

## 依赖
+ `PIL` or `Pillow`

## 注意
+ 当前需要在浏览器先登录一次，然后才能用机器人登录成功。

## 快速开始
+ 安装Python \> 2.6
+ 安装依赖（或者在命令行运行python setup.py develop）
+ 直接运行`run.py`
+ 等待弹出二维码进行扫描登陆，或手动打开脚本所在目录的v.jpg进行扫描。
+ 控制台不在输出登录确认的log的时候就登录成功了
+ 首次登陆过后，以后的登陆会尝试使用保存的cookie进行自动登录（失败后会一直loop）
+ 配置插件之后，才能使用QQBot的调教功能（参见下方插件配置）

## Feature

+ 二维码登录
+ 插件支持，支持原生Python Package，支持插件热 启用/关闭
+ 群消息，私聊消息，通知消息接收和发送

### 内置插件

+ 图灵机器人（需要安装requests库）
+ 插件管理器
+ Satoru（简单的吐槽机器人）

## 插件配置
### 载入一个插件

+ 将插件放置到smart_qq_plugins目录下
+ 复制plugin.json.example为plugin.json，然后修改启动的plugin_on，里面是启用的插件列表
，插件名称为你的PythonPackage或者插件文件的名字，默认启用了satoru和manager

## 已知问题
+ <s>加载多个插件后，可以接受消息，但无法正确发送(resolved)</s>

## RoadMap

+ 支持每个插件的单独配置文件
+ 优化发消息和Bot类（delayed）

## ChangeLog

+ 16.04.xx : 支持插件的激活和关闭

## Thanks to

+ [SmartQQBot](https://github.com/Yinzo/SmartQQBot)

## Contributors

+ [winkidney](https://github.com/winkidney)
+ [Cheng Gu](https://github.com/gucheen)

