# coding: utf-8
import os
import sys


here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(here)

from smart_qq_bot.main import run

run()