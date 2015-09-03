# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import threading

from QQLogin import *
from Configs import *
from Msg import *
from HttpClient import *


class Pm:
    def __init__(self, operator, ip):
        assert isinstance(operator, QQ), "Pm's operator is not a QQ"
        self.__operator = operator
        if isinstance(ip, (int, long, str)):
            # 使用uin初始化
            self.tuin = ip
        elif isinstance(ip, PmMsg):
            self.tuin = ip.from_uin
        self.tid = self.__operator.uin_to_account(self.tuin)
        self.msg_id = int(random.uniform(20000, 50000))
        self.msg_list = []
        self.global_config = DefaultConfigs()
        self.private_config = PmConfig(self)
        self.update_config()
        self.process_order = [
            "command_0arg",
            "command_1arg",
            "repeat",
            "callout",
        ]
        logging.info(str(self.tid) + "私聊已激活, 当前执行顺序： " + str(self.process_order))

    def update_config(self):
        use_private_config = bool(self.private_config.conf.getint("pm", "use_private_config"))
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
                if bool(self.config.conf.getint("pm", func)):
                    logging.info("evaling " + func)
                    if eval("self." + func)(msg):
                        logging.info("msg handle finished.")
                        self.msg_list.append(msg)
                        return func
            except ConfigParser.NoOptionError as er:
                logging.warning(er, "没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数")
        self.msg_list.append(msg)

    def reply(self, reply_content, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
        rsp = ""
        try:
            req_url = "http://d.web2.qq.com/channel/send_buddy_msg2"
            data = (
                ('r', '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(self.tuin, self.__operator.client_id, self.msg_id + 1, self.__operator.psessionid, fix_content)),
                ('clientid', self.__operator.client_id),
                ('psessionid', self.__operator.psessionid)
            )
            rsp = HttpClient().Post(req_url, data, self.__operator.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
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

    def repeat(self, msg):
        if len(self.msg_list) > 0 and self.msg_list[-1].content == msg.content:
            if str(msg.content).strip() not in ("", " ", "[图片]", "[表情]"):
                logging.info(str(self.tid) + " repeating, trying to reply " + str(msg.content))
                self.reply(msg.content)
                return True
        return False

    def command_0arg(self, msg):
        # webqq接受的消息会以空格结尾
        match = re.match(r'^(?:!|！)([^\s\{\}]+)\s*$', msg.content)
        if match:
            command = str(match.group(1))
            logging.info("command format detected, command: " + command)

        return False

    def command_1arg(self, msg):
        match = re.match(r'^(?:!|！)([^\s\{\}]+)(?:\s?)\{([^\s\{\}]+)\}\s*$', msg.content)
        if match:
            command = str(match.group(1))
            arg1 = str(match.group(2))
            logging.info("command format detected, command:{0}, arg1:{1}".format(command, arg1))

        return False
