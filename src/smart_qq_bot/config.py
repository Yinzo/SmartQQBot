# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import logging
import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SMART_QQ_REFER = "http://d1.web2.qq.com/proxy.html?v=20030916001&callback=1&id=2"
SMART_QQ_URL = "http://w.qq.com/"
QR_CODE_FNAME = "v.jpg"
QR_CODE_PATH = "./" + QR_CODE_FNAME

DEFAULT_PLUGIN_CONFIG = "config/plugin.json"

COOKIE_FILE = 'cookie/cookie.data'

SSL_VERIFY = True

def init_logging(logger, log_level=logging.DEBUG):
    assert isinstance(logger, logging.Logger)

    log_format = '[%(levelname)s] %(asctime)s  %(filename)s line %(lineno)d: %(message)s'
    date_fmt = '%a, %d %b %Y %H:%M:%S'
    formatter = logging.Formatter(log_format, date_fmt)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

