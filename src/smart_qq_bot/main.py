# -*- coding: utf-8 -*-
import logging
import socket
import sys

from smart_qq_bot.app import bot, plugin_manager
from smart_qq_bot.handler import MessageObserver
from smart_qq_bot.messages import mk_msg
from smart_qq_bot.excpetions import ServerResponseEmpty

def patch():
    reload(sys)
    sys.setdefaultencoding("utf-8")


def run():
    patch()

    logging.info("Initializing...")
    plugin_manager.load_plugin()
    bot.login()
    observer = MessageObserver(bot)
    while True:
        try:
            msg_list = bot.check_msg()
            if msg_list is not None:
                observer.handle_msg_list(
                    [mk_msg(msg) for msg in msg_list]
                )
        except ServerResponseEmpty:
            continue
        except (socket.timeout, IOError):
            logging.warning("Message pooling timeout, retrying...")
        except Exception:
            logging.exception("Exception occurs when checking msg.")

if __name__ == "__main__":
    run()

