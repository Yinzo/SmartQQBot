# -*- coding: utf-8 -*-

import json
import time
import random

from Configs import *
from Msg import *
from HttpClient import *


class Group:

    def __init__(self, operator, ip):
        if isinstance(ip, (int, long, str)):
            # 使用uin初始化
            self.guin = ip
            self.gid = ""
        elif isinstance(ip, GroupMsg):
            self.guin = ip.from_uin
            self.gid = ip.info_seq
        self.msg_id = int(random.uniform(20000, 50000))
        self.__operator = operator
        self.member_list = []
        self.msg_list = []
        self.follow_list = []
        self.tucao_dict = {}
        self.global_config = Configs()
        self.private_config = GroupConfig(self)
        self.handle_function_list = [
            'repeat',
            'callout',
        ]
        print str(self.gid) + "群已激活"

    def handle(self, msg):
        print "handling."
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.handle_function_list:
            # if func in dirs:
                # 此处的eval虽然有注入风险，但是进行输入的来源是conf文件
                # 而拥有修改conf的权限时已经没有必要进行python注入了。
            print "evaling " + func
            if eval("self." + func)(msg):
                return func

    def reply(self, reply_content, fail_times=0):
        last_fail_times = fail_times

        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
        rsp = ""
        try:
            req_url = "http://d.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r', '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(self.guin, self.__operator.ClientID, self.msg_id + 1, self.__operator.PSessionID, fix_content)),
                ('clientid', self.__operator.ClientID),
                ('psessionid', self.__operator.PSessionID)
            )
            rsp = HttpClient().Post(req_url, data, self.__operator.nowConfig.connect_referer)
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
            print "Reply response: " + str(rsp_json)
            self.msg_id += 1
            return rsp_json
        except:
            if last_fail_times < 5:
                # loggin.error("Response Error.Wait for 2s and Retrying."+str(lastFailTimes))
                # logging.info(rsp)
                print "Response Error.Wait for 2s and Retrying." + str(last_fail_times)
                print rsp
                last_fail_times += 1
                time.sleep(2)
                self.reply(reply_content, last_fail_times + 1)
            else:
                print "Response Error over 5 times.Exit."
                print "Content:" + str(reply_content)
                # logging.error("Response Error over 5 times.Exit.")
                # raise ValueError(rsp)
                return False

    def callout(self, msg):
        if "智障机器人" in msg.content:
            print "calling out, trying to reply...."
            self.reply("干嘛（‘·д·）")
            print str(self.gid) + "有人叫我"
            return True
        return False

    def repeat(self, msg):
        if len(self.msg_list) > 0 and self.msg_list[-1].content == msg.content and str(msg.content).strip() != '' and msg.content != ' ':
            if "[图片]" != msg.content or "[表情]" != msg.content:
                self.reply(msg.content)
                print "群" + str(self.gid) + "已复读：{" + str(msg.content) + "}"
                return True
        return False
