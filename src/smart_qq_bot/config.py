# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import logging
import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SMART_QQ_REFER = "http://d1.web2.qq.com/proxy.html?v=20030916001&callback=1&id=2"
SMART_QQ_URL = "http://w.qq.com/"
QR_CODE_PATH = "./v.jpg"

DEFAULT_PLUGIN_CONFIG = "config/plugin.json"


def init_logging(log_level=logging.INFO):
    log_format = '[%(levelname)s] %(asctime)s  %(filename)s line %(lineno)d: %(message)s'
    date_fmt = '%a, %d %b %Y %H:%M:%S'
    logging.basicConfig(
        format=log_format,
        datefmt=date_fmt,
        level=log_level,
    )