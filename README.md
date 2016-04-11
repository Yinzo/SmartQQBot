QBot
=========

## 依赖
+ `PIL` or `Pillow`

## 注意
+ 当前需要在浏览器先登录一次，然后才能用机器人登录成功。

## 快速开始
+ 安装依赖（或者运行python setup.py develop）
+ 直接运行`run.py`
+ 等待弹出二维码进行扫描登陆，或手动打开脚本所在目录的v.jpg进行扫描。
+ 控制台不在输出登录确认的log的时候就登录成功了
+ 首次登陆过后，以后的登陆会尝试使用保存的cookie进行自动登录（失败后会一直loop）

## 插件
+ 复制config.json.example为config.json，然后修改启动的plugin_on，里面是启用的插件列表

## 已知问题
+ <s>加载多个插件后，可以接受消息，但无法正确发送(resolved)</s>

## RoadMap
+ 支持每个插件的单独配置文件
+ <s>支持插件的激活和关闭</s>
+ 优化发消息和Bot类（待定）

## Thanks to
* [SmartQQBot](https://github.com/Yinzo/SmartQQBot)

