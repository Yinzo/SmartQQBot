# coding: utf-8
from random import randint
import re
from smart_qq_bot.handler import (
    list_handlers,
    list_active_handlers,
    activate,
    inactivate,
)
from smart_qq_bot.logger import logger
from smart_qq_bot.messages import GroupMsg, PrivateMsg
from smart_qq_bot.signals import on_all_message, on_bot_inited


@on_all_message(name="KfPlugin")
def sample_plugin(msg, bot):
    msg_id = randint(1, 10000)
    if isinstance(msg, PrivateMsg):
        if msg.content=="KF":
            bot.send_friend_msg("msg", msg.from_uin, msg_id)
