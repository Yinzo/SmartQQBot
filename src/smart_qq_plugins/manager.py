# coding: utf-8
import re
from smart_qq_bot.handler import (
    list_handlers,
    list_active_handlers,
    activate,
    inactivate,
)
from smart_qq_bot.logger import logger
from smart_qq_bot.signals import on_all_message, on_bot_inited, on_private_message

cmd_hello = re.compile(r"!hello")
cmd_list_plugin = re.compile(r"!list_plugin")
cmd_inactivate = re.compile(r"!inactivate \{(.*?)\}")
cmd_activate = re.compile(r"!activate \{(.*?)\}")


def do_activate(text):
    result = re.findall(cmd_activate, text)
    if result:
        activate(result[0])
        return "Function [%s] activated successfully" % result[0]


def do_inactivate(text):
    re.findall(cmd_inactivate, text)
    result = re.findall(cmd_inactivate, text)
    if result:
        inactivate(result[0])
        return "Function [%s] inactivated successfully" % result[0]


def do_hello(text):
    if re.match(cmd_hello, text):
        return "大头沙皮!"


def do_list_plugin(text):
    if re.match(cmd_list_plugin, text):
        return "All: %s\n\nActive: %s" % (
            str(list_handlers()), str(list_active_handlers())
        )


@on_bot_inited("PluginManager")
def manager_init(bot):
    logger.info("Plugin Manager is available now:)")


@on_all_message(name="PluginManger[hello]")
def hello_bot(msg, bot):
    result = do_hello(msg.content)
    if result is not None:
        return bot.reply_msg(msg, result)


@on_private_message(name="PluginManager[manage_tools]")
def manage_tool(msg, bot):
    private_handlers = (
        do_inactivate, do_activate, do_list_plugin
    )
    for handler in private_handlers:
        result = handler(msg.content)
        if result is not None:
            return bot.reply_msg(msg, result)
