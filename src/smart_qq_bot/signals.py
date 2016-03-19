# coding: utf-8
from functools import wraps

from smart_qq_bot.handler import (
    register,
)
from smart_qq_bot.messages import (
    GROUP_MSG,
)


def on_all_message(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    register(wrapper)
    return wrapper


def on_group_message(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    register(wrapper, GROUP_MSG)
    return wrapper