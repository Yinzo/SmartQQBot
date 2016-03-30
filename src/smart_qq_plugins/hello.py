# coding: utf-8
from random import randint
import re

from smart_qq_bot.signals import on_group_message


@on_group_message
def hello_bot(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    if re.match(r"!hello", msg.content):
        bot.send_qun_msg(msg.from_uin, "老脏沙皮！", msg_id=randint(1, 1000))