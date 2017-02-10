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

