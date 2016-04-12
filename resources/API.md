API Reference
-------------------


## 可用的Signals

```python
from smart_qq_bot.signals import (
    on_all_message,
    on_group_message,
    on_private_message,
)
```

## 插件管理相关

```
from smart_qq_bot.handler import (
    list_handlers,  # List all plugins
    list_active_handlers,  # List current active plugins
    activate,  # Activate a plugin by its name
    inactivate,  # Inactivate a plugin by its name
)
```