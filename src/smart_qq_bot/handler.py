# coding: utf-8
from collections import defaultdict, namedtuple
from threading import Thread

from six import iteritems
from six.moves.queue import Queue
from six.moves import range

from smart_qq_bot.bot import QQBot
from smart_qq_bot.logger import logger
from smart_qq_bot.excpetions import (
    MsgProxyNotImplementError,
    InvalidHandlerType,
)
from smart_qq_bot.messages import MSG_TYPE_MAP

__all__ = (
    # functions
    "register",

    # objects
    "MessageObserver",
)


_registry = defaultdict(list)
_active = set()

RAW_TYPE = "raw_message"

MSG_TYPES = list(MSG_TYPE_MAP.keys())
MSG_TYPES.append(RAW_TYPE)


Handler = namedtuple("Handler", ("func", "name"))
Task = namedtuple("Task", ("func", "name", "kwargs"))


def register(func, msg_type=None, dispatcher_name=None, active_by_default=True):
    """
    Register handler to RAW if msg_type not given.
    :type func: callable
    :type msg_type: str or unicode
    """
    if msg_type and msg_type not in MSG_TYPE_MAP:
        raise InvalidHandlerType(
            "Invalid message type [%s]: type should be in %s"
            % (msg_type, str(MSG_TYPES))
        )
    handler = Handler(func=func, name=dispatcher_name)
    if msg_type is None:
        _registry[RAW_TYPE].append(handler)
    else:
        _registry[msg_type].append(handler)
    if active_by_default:
        _active.add(dispatcher_name)


def list_handlers():
    handler_list = []
    for _, handlers in iteritems(_registry):
        handler_list.extend(
            [handler.name for handler in handlers]
        )
    return handler_list


def list_active_handlers():
    return _active


def is_active(dispatcher_name):
    return dispatcher_name in _active


def inactivate(dispatcher_name):
    try:
        _active.remove(dispatcher_name)
        logger.info(
            'Plugin %s inactivated.'
            % dispatcher_name
        )
    except KeyError:
        logger.info(
            'Plugin name %s does not exist, failed to inactivate.'
            % dispatcher_name
        )


def activate(dispatcher_name):
    _active.add(dispatcher_name)
    logger.info(
        'Plugin %s activated.'
        % dispatcher_name
    )


class Worker(Thread):

    def __init__(
            self, queue, group=None,
            target=None, name=None, args=(),
            kwargs=None,
    ):
        """
        :type queue: Queue
        """
        super(Worker, self).__init__(
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
        )
        self.queue = queue
        self._stopped = False
        self.worker_timeout = 20
        self._stop_done = False

    def run(self):
        while True:
            if self._stopped:
                break
            task = self.queue.get()
            try:
                task.func(**task.kwargs)
            except Exception:
                logger.exception(
                    "Error occurs when running task from plugin [%s]."
                    % task.name
                )
        self._stop_done = True

    def stop(self):
        self._stopped = True


class MessageObserver(object):

    _registry = _registry

    def __init__(self, bot, workers=5):
        """
        :type bot: smart_qq_bot.bot.QQBot
        """
        if not isinstance(bot, QQBot):
            raise MsgProxyNotImplementError(
                "bot should be instance of QQBot"
            )
        self.bot = bot
        self.handler_queue = Queue()
        self.workers = [Worker(self.handler_queue) for i in range(workers)]
        for worker in self.workers:
            worker.setDaemon(True)
            worker.start()

    def handle_msg_list(self, msg_list):
        """
        :type msg_list: list or tuple
        """
        for msg in msg_list:
            self._handle_one(msg)

    def _handle_one(self, msg):
        """
        :type msg: smart_qq_bot.messages.QMessage
        """
        handlers = self._registry[msg.type]

        for handler in handlers + self._registry[RAW_TYPE]:
            if is_active(handler.name):
                self.handler_queue.put(
                    Task(
                        func=handler.func,
                        name=handler.name,
                        kwargs={"msg": msg, "bot": self.bot}
                    )
                )