# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import json
import logging
import socket
import sys

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
    while True:
        try:
            bot.check_msg()
        except socket.timeout as e:
            logging.warning("Message pooling timeout, retrying...")
            continue
        except Exception:
            logging.exception("Exception occurs when checking msg.")
            continue

if __name__ == "__main__":
    run()

