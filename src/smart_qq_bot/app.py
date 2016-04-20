# coding: utf-8

from smart_qq_bot.bot import QQBot
from smart_qq_bot.plugin import PluginManager

__all__ = (
    "bot"
)

bot = QQBot()
plugin_manager = PluginManager(load_now=False)