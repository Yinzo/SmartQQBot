# coding: utf-8
from random import randint
import re
from smart_qq_bot.handler import (
    list_handlers,
    list_active_handlers,
    activate,
    inactivate,
)
from smart_qq_bot.messages import GroupMsg, PrivateMsg

from smart_qq_bot.signals import on_all_message


cmd_hello = re.compile(r"!hello")
cmd_list_plugin = re.compile(r"!list_plugin")
cmd_inactivate = re.compile(r"!inactivate \{(.*?)\}")
cmd_activate = re.compile(r"!activate \{(.*?)\}")


def do_activate(text):
    result = re.findall(cmd_activate, text)
    if result:
        activate(result[0])
        return "Plugin [%s] activated successfully" % result[0]


def do_inactivate(text):
    re.findall(cmd_inactivate, text)
    result = re.findall(cmd_inactivate, text)
    if result:
        inactivate(result[0])
        return "Plugin [%s] inactivated successfully" % result[0]


def do_hello(text):
    if re.match(cmd_hello, text):
        return "大头沙皮!"


def do_list_plugin(text):
    if re.match(cmd_list_plugin, text):
        return "All: %s, Active: %s" % (
            str(list_handlers()), str(list_active_handlers())
        )


@on_all_message(name="PluginManger")
def hello_bot(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    msg_id = randint(1, 10000)

    group_handlers = (
        do_hello,
    )
    private_handlers = (
        do_inactivate, do_activate, do_list_plugin
    )
    if isinstance(msg, GroupMsg):
        for handler in group_handlers:
            result = handler(msg.content)
            if result is not None:
                return bot.send_qun_msg(msg.from_uin, result, msg_id)
    elif isinstance(msg, PrivateMsg):
        for handler in private_handlers:
            result = handler(msg.content)
            if result is not None:
                return bot.send_buddy_msg(msg.from_uin, result, msg_id)