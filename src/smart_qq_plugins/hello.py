# coding: utf-8
from random import randint
import re
from smart_qq_bot.messages import GroupMsg

from smart_qq_bot.signals import on_all_message


@on_all_message(name="Test Bot")
def hello_bot(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    if re.match(r"!hello", msg.content):
        msg_id = randint(1, 10000)
        if isinstance(msg, GroupMsg):
            bot.send_qun_msg(msg.from_uin, "大头沙皮！", msg_id)
        else:
            bot.send_buddy_msg(msg.from_uin, "大头沙皮！", msg_id)