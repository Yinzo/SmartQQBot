# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import logging
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SMART_QQ_REFER = "http://d1.web2.qq.com/proxy.html?v=20030916001&callback=1&id=2"
SMART_QQ_URL = "http://w.qq.com/"
QR_CODE_PATH = "./v.jpg"
SAVE_DATA_DIR = "./data/tucao_save/"


def init_logging(log_level=logging.INFO):
    log_format = '[%(levelname)s] %(asctime)s  %(filename)s line %(lineno)d: %(message)s'
    log_file = 'smartqq.log'
    date_fmt = '%a, %d %b %Y %H:%M:%S'

    root_logger = logging.getLogger()

    handlers = [logging.StreamHandler(), logging.FileHandler(log_file)]
    formatter = logging.Formatter(log_format, date_fmt)
    for handler in handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
