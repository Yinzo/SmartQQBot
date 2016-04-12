# coding: utf-8
from functools import wraps

from smart_qq_bot.handler import (
    register,
)
from smart_qq_bot.messages import (
    GROUP_MSG,
    PRIVATE_MSG)


def _real_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def _mk_wrapper(msg_type):
    def _register_func(func=None, name=None):
        if func is not None:
            wrapped = _real_wrapper(func)
            register(wrapped, msg_type, func.__name__)
            return wrapped
        else:
            def wrapper(new_func):
                wrapped = _real_wrapper(new_func)
                register(wrapped, msg_type, name or new_func.__name__)
            return wrapper
    return _register_func


on_all_message = _mk_wrapper(None)
on_group_message = _mk_wrapper(GROUP_MSG)
on_private_message = _mk_wrapper(PRIVATE_MSG)