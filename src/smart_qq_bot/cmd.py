# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import logging
import socket
import sys
from time import sleep

from smart_qq_bot.config import init_logging
from smart_qq_bot.login import QQ


def patch():
    reload(sys)
    sys.setdefaultencoding("utf-8")


def run():
    patch()
    init_logging(logging.DEBUG)
    bot = QQ()
    bot.login()
    while 1:
        try:
            new_msg_list = bot.check_msg()
        except socket.timeout as e:
            logging.warning("Message pooling timeout, retrying...")
            continue
        except Exception:
            logging.exception("Exception occurs when checking msg.")
            continue
        new_msg = new_msg_list[0]
        bot.send_qun_msg(new_msg['value']['from_uin'], "hello", new_msg['value']["msg_id"])

if __name__ == "__main__":
    run()

