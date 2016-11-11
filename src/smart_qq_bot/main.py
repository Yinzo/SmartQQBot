# -*- coding: utf-8 -*-
import argparse
import logging
import os
import socket
import sys

from six import PY2
from six import iteritems

from smart_qq_bot.config import COOKIE_FILE
from smart_qq_bot.logger import logger
from smart_qq_bot.app import bot, plugin_manager
from smart_qq_bot.handler import MessageObserver
from smart_qq_bot.messages import mk_msg
from smart_qq_bot.excpetions import ServerResponseEmpty, NeedRelogin
from smart_qq_bot.signals import bot_inited_registry


def patch():
    if PY2:
        reload(sys)
        sys.setdefaultencoding("utf-8")


def clean_cookie():
    if os.path.isfile(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    logger.info("Cookie file removed.")


def run_http_daemon(host="0.0.0.0", port=8888):
    from threading import Thread
    from smart_qq_bot.httpserver import run_server
    daemon = Thread(
        target=run_server,
        kwargs={"host": host, "port": port}
    )
    daemon.setDaemon(True)
    daemon.start()


def main_loop(no_gui=False, new_user=False, debug=False, http=False):
    patch()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if http:
        run_http_daemon()
    logger.info("Initializing...")
    plugin_manager.load_plugin()
    if new_user:
        clean_cookie()
    bot.login(no_gui)
    observer = MessageObserver(bot)
    for name, func in iteritems(bot_inited_registry):
        try:
            func(bot)
        except Exception:
            logging.exception(
                "Error occurs while loading plugin [%s]." % name
            )
    while True:
        try:
            msg_list = bot.check_msg()
            if msg_list is not None:
                observer.handle_msg_list(
                    [mk_msg(msg, bot) for msg in msg_list]
                )
        except ServerResponseEmpty:
            continue
        except (socket.timeout, IOError):
            logger.warning("Message pooling timeout, retrying...")
        except NeedRelogin:
            exit(0)
        except Exception:
            logger.exception("Exception occurs when checking msg.")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-gui",
        action="store_true",
        default=False,
        help="Whether display QRCode with tk and PIL."
    )
    parser.add_argument(
        "--http",
        action="store_true",
        default=False,
        help="Whether launch a bottle server to serve qrcode."
    )
    parser.add_argument(
        "--new-user",
        action="store_true",
        default=False,
        help="Logout old user first(by clean the cookie file.)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Switch to DEBUG mode for better view of requests and responses."
    )
    args = parser.parse_args()
    main_loop(**vars(args))


if __name__ == "__main__":
    run()

