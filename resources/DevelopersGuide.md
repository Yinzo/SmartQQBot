Developer's Guide
-----------------

QQBot提供的二次开发接口主要是针对插件，基础框架的贡献请提Issue和PullRequest

## 插件开发

### How Plugin Works
插件本质上是一个Python文件或者Python模块，通过将注册事件监听器到MessageObserver，
在收到消息的时候，调用插件文件内注册好的Callback

### Quick Start

#### 开发内置插件

1. 创建一个文件 `sample_plugin.py`，放置到smart_qq_plugins文件夹内

```python
# coding: utf-8
from random import randint

from smart_qq_bot.messages import GroupMsg, PrivateMsg
from smart_qq_bot.signals import on_all_message, on_bot_inited
from smart_qq_bot.logger import logger


@on_bot_inited("PluginManager")
def manager_init(bot):
    logger.info("Plugin Manager is available now:)")

@on_all_message(name="SamplePlugin")
def sample_plugin(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    msg_id = randint(1, 10000)
    
    # 发送一条群消息
    if isinstance(msg, GroupMsg):
        bot.send_group_msg("msg", msg.from_uin, msg_id)
    # 发送一条私聊消息
    elif isinstance(msg, PrivateMsg):
        bot.send_friend_msg("msg", msg.from_uin, msg_id)
```

2. 在plugin.json中，`plugin_on`字段中，填入新插件名字，文件可能是这样
```json
{
  "plugin_packages": [],
  "plugin_on": [
      "manager",
      "satoru",
      "sample_plugin"
  ]
}
```

3. 启动机器人，会在console看到插件已经载入

#### 将一个Python包作为插件使用

1. 参考内置插件的开发方式，使用相同的方式写插件，但是作为一个独立的Python包。
唯一要注意的地方是，确保Python在import这个Package的时候，所有的"on_all_message"一类
的信号装饰器必须全部被执行，否则将无法成功注册这个插件。

2. 在plugin.json中的`plugin_packages`, 增加一个字段`your_plugin_package_name`,
增加后的文件可能是这样的（包名必须在PythonPath里，否则无法导入）.
```
{
  "plugin_packages": ['your_plugin_package_name'],
  "plugin_on": [
      "manager",
      "satoru"
  ]
}
```

3. 启动机器人，可以在console里看到插件被载入
