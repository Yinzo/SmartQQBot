# coding: utf-8
import logging

from smart_qq_bot.bot import QQBot
from smart_qq_bot.plugin import PluginManager
from smart_qq_bot.config import init_logging

__all__ = (
    "bot"
)
init_logging(logging.DEBUG)
bot = QQBot()
plugin_manager = PluginManager(load_now=False)