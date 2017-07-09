API Reference
-------------------


## 可用的Signals

```python
from smart_qq_bot.signals import (
    on_all_message,
    on_group_message,
    on_private_message,
    on_bot_inited,
)
```

其中 `on_bot_inited` 用法略有不同，以 PluginManager 的初始化为例，其插件函数只有一个 `bot` 参数，而不像其它 signal 还有 `msg` 参数

```python
@on_bot_inited("PluginManager")
def manager_init(bot):
    logger.info("Plugin Manager is available now:)")

```

### 选择接收自己发出的消息
机器人在群聊中回复消息的时候，自己也会接收到自己发出的消息。这个消息在插件框架中默认是直接忽略的，如果你需要接受并处理它，请在 Signals 装饰器中指定 `accept_self` 参数为 `True`，这样机器人收到自己的消息的时候也将会转交给这一插件处理。

示例：

```python
@on_group_message(name='self_test', accept_self=True)
def test2(msg, bot):
    reply = bot.reply_msg(msg, return_function=True)
    prefix = 'test_self'
    if msg.content.startswith(prefix):
        reply("#测试内容：{}".format(msg.content[len(prefix):]))

    if bot.is_self_msg(msg) and msg.content.startswith('#测试内容：'):
        reply("成功收到了自己的消息: {}".format(msg.content[len("#测试内容："):]))
```


## 插件管理相关

可通过此 API 对其它插件进行 activate 和 inactivate
```
from smart_qq_bot.handler import (
    list_handlers,  # List all plugins
    list_active_handlers,  # List current active plugins
    activate,  # Activate a plugin by its name
    inactivate,  # Inactivate a plugin by its name
)
```

## 消息回复相关
+ `bot.reply_msg`函数

	```python
	def reply_msg(self, msg, reply_content=None, return_function=False):
		"""
		:type msg: QMessage类, 例如 GroupMsg, PrivateMsg, SessMsg
		:type reply_content: str, 回复的内容.
		:return: 服务器的响应内容. 如果 return_function 为 True, 则返回的是一个仅有 reply_content 参数的便捷回复函数.
		"""
	```

