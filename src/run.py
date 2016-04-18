# coding: utf-8
import os
import sys
import logging


here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(here)

from smart_qq_bot.main import run

try:
    run()
except KeyboardInterrupt:
    logging.info("User stop. exit.")
    exit(0)