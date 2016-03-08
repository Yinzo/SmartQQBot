# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import threading
import random

from QQLogin import *
from Configs import *
from Msg import *
from HttpClient import *


class Sess:
    def __init__(self, operator, sess_msg):
        assert isinstance(operator, QQ), "Pm's operator is not a QQ"
        self.__operator = operator
        if not isinstance(sess_msg, SessMsg):
            raise TypeError("RUNTIMELOG Received not a sess msg.")
        self.tuin = sess_msg.from_uin
        self.tid = self.__operator.uin_to_account(self.tuin)
        self.id = sess_msg.id
        self.service_type = sess_msg.service_type
        self.msg_id = int(random.uniform(20000, 50000))
        self.group_sig = self.get_group_sig()
        self.msg_list = []
        self.global_config = DefaultConfigs()
        self.private_config = SessConfig(self)
        self.config = self.global_config
        self.update_config()
        self.process_order = [
            "callout",
        ]
        logging.info("RUNTIMELOG " + str(self.tid) + "临时聊天已激活, 当前执行顺序： " + str(self.process_order))

    def update_config(self):
        use_private_config = bool(self.private_config.conf.getint("sess", "use_private_config"))
        if use_private_config:
            self.config = self.private_config
        else:
            self.config = self.global_config
        self.config.update()

    def handle(self, msg):
        self.update_config()
        logging.info("RUNTIMELOG msg handling.")
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.process_order:
            try:
                if bool(self.config.conf.getint("sess", func)):
                    logging.info("RUNTIMELOG evaling " + func)
                    if eval("self." + func)(msg):
                        logging.info("RUNTIMELOG msg handle finished.")
                        self.msg_list.append(msg)
                        return func
            except ConfigParser.NoOptionError:
                logging.warning("RUNTIMELOG 没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数")
        self.msg_list.append(msg)

    def get_group_sig(self, fail_time=0):
        if fail_time > 10:
            raise IOError("RUNTIMELOG can not get group_sig, check the internet connection.")
        ts = time.time()
        while ts < 1000000000000:
            ts *= 10
        ts = int(ts)
        try:
            logging.info("RUNTIMELOG trying to get group_sig")
            group_sig = HttpClient().Get(
                'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                    self.id,
                    self.tuin,
                    self.__operator.client_id,
                    self.__operator.psessionid,
                    self.service_type,
                    ts,
                ), self.__operator.default_config.conf.get('global', 'connect_referer'))
            logging.debug("RESPONSE group_sig response:  " + str(group_sig))
            group_sig = json.loads(group_sig)['result']['value']
            if group_sig == "":
                raise ValueError("RUNTIMELOG Receive a None when getting group sig")
            return group_sig
        except BaseException, e:
            logging.warning("RUNTIMELOG Getting group sig met an error: " + str(e) + " Retrying...")
            return self.get_group_sig(fail_time + 1)

    def reply(self, reply_content):
        self.msg_id += 1
        return self.__operator.send_sess_msg2(self.tuin, reply_content, self.msg_id, self.group_sig, self.service_type)

    def callout(self, msg):
        if "智障机器人" in msg.content:
            logging.info("RUNTIMELOG " + str(self.tid) + " calling me out, trying to reply....")
            self.reply("干嘛（‘·д·）")
            return True
        return False
