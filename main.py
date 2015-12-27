#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import sys

from MsgHandler import *

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
    bot = QQ()
    bot.login()
    bot_handler = MsgHandler(bot)
    while 1:
        try:
            new_msg = bot.check_msg()
        except socket.timeout, e:
            logging.warning("check msg timeout, retrying...")
            continue
        if new_msg is not None:
            bot_handler.handle(new_msg)
