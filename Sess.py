# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import threading

from QQLogin import *
from Configs import *
from Msg import *
from HttpClient import *


class Sess:
    def __init__(self, operator, sess_msg):
        assert isinstance(operator, QQ), "Pm's operator is not a QQ"
        self.__operator = operator
        if not isinstance(sess_msg, SessMsg):
            logging.error("Received not a sess msg.")
            raise TypeError("Received not a sess msg.")
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
        logging.info(str(self.tid) + "临时聊天已激活, 当前执行顺序： " + str(self.process_order))

    def update_config(self):
        use_private_config = bool(self.private_config.conf.getint("sess", "use_private_config"))
        if use_private_config:
            self.config = self.private_config
        else:
            self.config = self.global_config
        self.config.update()

    def handle(self, msg):
        self.update_config()
        logging.info("msg handling.")
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.process_order:
            try:
                if bool(self.config.conf.getint("sess", func)):
                    logging.info("evaling " + func)
                    if eval("self." + func)(msg):
                        logging.info("msg handle finished.")
                        self.msg_list.append(msg)
                        return func
            except ConfigParser.NoOptionError as er:
                logging.warning(er, "没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数")
        self.msg_list.append(msg)

    def get_group_sig(self, fail_time=0):
        if fail_time > 10:
            logging.error("can not get group_sig, check the internet connection.")
            raise IOError("can not get group_sig, check the internet connection.")
        ts = time.time()
        while ts < 1000000000000:
            ts *= 10
        ts = int(ts)
        try:
            logging.info("trying to get group_sig")
            group_sig = HttpClient().Get(
                'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                    self.id,
                    self.tuin,
                    self.__operator.client_id,
                    self.__operator.psessionid,
                    self.service_type,
                    ts,
                ), self.__operator.default_config.conf.get('global', 'connect_referer'))
            logging.debug("group_sig response:  " + str(group_sig))
            group_sig = json.loads(group_sig)['result']['value']
            if group_sig == "":
                logging.warning("Receive a None when getting group sig")
                raise ValueError("Receive a None when getting group sig")
            return group_sig
        except BaseException, e:
            logging.warning("Getting group sig met an error: " + str(e) + " Retrying...")
            return self.get_group_sig(fail_time + 1)

    def reply(self, reply_content, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
        rsp = ""
        try:
            req_url = "http://d.web2.qq.com/channel/send_sess_msg2"
            data = (
                ('r',
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                     self.tuin,
                     self.__operator.client_id,
                     self.msg_id + 1,
                     self.__operator.psessionid,
                     fix_content,
                     self.group_sig,
                     self.service_type)
                 ),
                ('clientid', self.__operator.client_id),
                ('psessionid', self.__operator.psessionid),
                ('group_sig', self.group_sig),
                ('service_type', self.service_type)
            )
            rsp = HttpClient().Post(req_url, data, self.__operator.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply sess chat error" + str(rsp_json['retcode']))
            logging.info("Reply successfully.")
            logging.debug("Reply response: " + str(rsp))
            self.msg_id += 1
            return rsp_json
        except:
            if fail_times < 5:
                logging.warning("Response Error.Wait for 2s and Retrying." + str(fail_times))
                logging.debug(rsp)
                time.sleep(2)
                self.reply(reply_content, fail_times + 1)
            else:
                logging.warning("Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False

    def callout(self, msg):
        if "智障机器人" in msg.content:
            logging.info(str(self.tid) + " calling me out, trying to reply....")
            self.reply("干嘛（‘·д·）")
            return True
        return False
