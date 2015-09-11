# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

from Group import *
from Pm import *
from Sess import *
import threading

logging.basicConfig(
    filename='smartqq.log',
    level=logging.DEBUG,
    format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


class MsgHandler:
    def __init__(self, operator):
        if not isinstance(operator, QQ):
            raise TypeError("Operator must be a logined QQ instance")

        self.__operator = operator
        self.process_threads = {}
        self.__group_list = {}
        self.__pm_list = {}
        self.__sess_list = {}

    def handle(self, msg_list):
        assert isinstance(msg_list, list), "msg_list is NOT a LIST"
        for msg in msg_list:
            # 仅处理程序管理层面上的操作 Only do the operation of the program management

            if not isinstance(msg, (Msg, Notify)):
                logging.error("Handler received a not a Msg or Notify instance.")
                raise TypeError("Handler received a not a Msg or Notify instance.")

            elif isinstance(msg, MsgWithContent):
                logging.info(str(self.__operator.get_account(msg)) + ":" + msg.content)

            if isinstance(msg, GroupMsg):
                # 判断群对象是否存在，info_seq实际上为群号
                if msg.info_seq not in self.__group_list:
                    self.__group_list[msg.info_seq] = Group(self.__operator, msg)
                    self.process_threads[msg.info_seq] = MsgHandleQueue(self.__group_list[msg.info_seq])
                    self.process_threads[msg.info_seq].start()
                    logging.debug("Now group list:  " + str(self.__group_list))

                tgt_group = self.__group_list[msg.info_seq]
                if len(tgt_group.msg_list) >= 1 and msg.seq == tgt_group.msg_list[-1].seq:
                    # 若如上一条seq重复则抛弃此条信息不处理
                    logging.info("消息重复，抛弃")
                    return

                tgt_group.msg_id = msg.msg_id

                self.process_threads[msg.info_seq].append(msg)

            elif isinstance(msg, PmMsg):
                tid = self.__operator.get_account(msg)
                if tid not in self.__pm_list:
                    self.__pm_list[tid] = Pm(self.__operator, msg)
                    self.process_threads[tid] = MsgHandleQueue(self.__pm_list[tid])
                    self.process_threads[tid].start()
                    logging.debug("Now pm thread list:  " + str(self.__pm_list))

                tgt_pm = self.__pm_list[tid]
                if len(tgt_pm.msg_list) >= 1 and msg.time == tgt_pm.msg_list[-1].time \
                        and msg.from_uin == tgt_pm.msg_list[-1].from_uin \
                        and msg.content == tgt_pm.msg_list[-1].content:
                    # 私聊没有seq可用于判断重复，只能抛弃同一个人在同一时间戳发出的内容相同的消息。
                    logging.info("消息重复，抛弃")
                    return

                tgt_pm.msg_id = msg.msg_id

                self.process_threads[tid].append(msg)

            elif isinstance(msg, SessMsg):
                tid = self.__operator.get_account(msg)
                if tid not in self.__sess_list:
                    self.__sess_list[tid] = Sess(self.__operator, msg)
                    self.process_threads[tid] = MsgHandleQueue(self.__sess_list[tid])
                    self.process_threads[tid].start()
                    logging.debug("Now sess thread list:  " + str(self.__sess_list))

                tgt_sess = self.__sess_list[tid]
                if len(tgt_sess.msg_list) >= 1 and msg.time == tgt_sess.msg_list[-1].time \
                        and msg.from_uin == tgt_sess.msg_list[-1].from_uin \
                        and msg.content == tgt_sess.msg_list[-1].content:
                    # 私聊没有seq可用于判断重复，只能抛弃同一个人在同一时间戳发出的同一内容的消息。
                    logging.info("消息重复，抛弃")
                    return
                tgt_sess.msg_id = msg.msg_id
                self.process_threads[tid].append(msg)

            elif isinstance(msg, InputNotify):
                self.__input_notify_handler(msg)

            elif isinstance(msg, BuddiesStatusChange):
                self.__buddies_status_change_handler(msg)

            elif isinstance(msg, KickMessage):
                self.__kick_message(msg)

            else:
                logging.warning("Unsolved Msg type :" + str(msg.poll_type))
                raise TypeError("Unsolved Msg type :" + str(msg.poll_type))

    def __input_notify_handler(self, msg):
        logging.info(str(self.__operator.get_account(msg)) + " is typing...")

    def __buddies_status_change_handler(self, msg):
        pass

    def __kick_message(self, msg):
        logging.warning(str(msg.to_uin) + " is kicked. Reason: " + str(msg.reason))
        logging.warning("[{0}]{1} is kicked. Reason:  {2}".format(
            str(msg.to_uin),
            self.__operator.username,
            str(msg.reason),
        ))
        raise KeyboardInterrupt("Kicked")


class MsgHandleQueue(threading.Thread):

    def __init__(self, handler):
        super(MsgHandleQueue, self).__init__()
        self.handler = handler
        self.msg_queue = []
        self.setDaemon(True)

    def run(self):
        while 1:
            if len(self.msg_queue):
                self.handler.handle(self.msg_queue.pop(0))
                logging.debug("queue handling.Now queue length:" + str(len(self.msg_queue)))
            else:
                time.sleep(1)

    def append(self, msg):
        self.msg_queue.append(msg)
