# -*- coding: utf-8 -*-

from QQLogin import *
from Notify import *
from Group import *


class MsgHandler:

    def __init__(self, operator):
        if not isinstance(operator, QQ):
            raise TypeError("Operator must be a logined QQ instance")

        self.__operator = operator
        self.__group_list = {}
        self.__pm_list = {}
        self.__sess_list = {}

    def handle(self, msg_list):
        assert isinstance(msg_list, list), "msg_list is NOT a LIST"
        for msg in msg_list:
            # 仅处理程序管理层面上的操作 Only do the operation of the program management
            if not isinstance(msg, (Msg, Notify)):
                raise TypeError("Handler received a not a Msg or Notify instance.")

            elif isinstance(msg, MsgWithContent):
                print str(self.__operator.get_account(msg)) + ":" + msg.content

            if isinstance(msg, GroupMsg):
                if msg.info_seq not in self.__group_list:
                    self.__group_list[msg.info_seq] = Group(self.__operator, msg)

                tgt_group = self.__group_list[msg.info_seq]

                if len(tgt_group.msg_list) >= 1 and msg.seq == tgt_group.msg_list[-1].seq:
                    # 若如上一条seq重复则抛弃此条信息不处理
                    return

                tgt_group.msg_id = msg.msg_id
                self.__group_list[msg.info_seq].handle(msg)
                tgt_group.msg_list.append(msg)

            elif isinstance(msg, PmMsg):
                self.__pm_msg_handler(msg)

            elif isinstance(msg, SessMsg):
                self.__sess_msg_handler(msg)

            elif isinstance(msg, InputNotify):
                self.__input_notify_handler(msg)

            elif isinstance(msg, BuddiesStatusChange):
                self.__buddies_status_change_handler(msg)

            elif isinstance(msg, KickMessage):
                self.__kick_message(msg)

            else:
                raise TypeError("Unsolved Msg type :" + str(msg.poll_type))

    def __pm_msg_handler(self, msg):
        print "pm msg received"
        self.reply_msg(msg, "Received")

    def __sess_msg_handler(self, msg):
        print "sess msg received"
        self.reply_msg(msg, "Received")

    def __input_notify_handler(self, msg):
        print str(self.__operator.get_account(msg)) + " is typing..."

    def __buddies_status_change_handler(self, msg):
        pass

    def __kick_message(self, msg):
        print str(msg.to_uin) + " is kicked. Reason: " + str(msg.reason)
        raise KeyboardInterrupt("Kicked")

    def reply_msg(self, received_msg, reply_content, fail_times=0):
        last_fail_times = fail_times

        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
        rsp = ""
        req_url = ""
        data = ""
        try:
            if isinstance(received_msg, SessMsg):
                ts = time.time()
                while ts < 1000000000000:
                    ts *= 10
                ts = int(ts)
                group_sig = ""
                try:
                    group_sig = json.loads(HttpClient().Get('http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(received_msg.id, received_msg.from_uin, self.__operator.ClientID, self.__operator.PSessionID, received_msg.service_type, ts), self.__operator.nowConfig.connect_referer))
                    if group_sig == "":
                        raise ValueError("Receive a None when getting group sig")
                except BaseException, e:
                    print "Getting group sig met an error: ", e
                req_url = "http://d.web2.qq.com/channel/send_sess_msg2"
                data = (
                    ('r', '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(received_msg.from_uin, self.__operator.ClientID, received_msg.msg_id + 1, self.__operator.PSessionID, fix_content, group_sig, received_msg.service_type)),
                    ('clientid', self.__operator.ClientID),
                    ('psessionid', self.__operator.PSessionID),
                    ('group_sig', group_sig),
                    ('service_type', received_msg.service_type)
                )
            elif isinstance(received_msg, PmMsg):
                req_url = "http://d.web2.qq.com/channel/send_buddy_msg2"
                data = (
                    ('r', '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(received_msg.from_uin, self.__operator.ClientID, received_msg.msg_id + 1, self.__operator.PSessionID, fix_content)),
                    ('clientid', self.__operator.ClientID),
                    ('psessionid', self.__operator.PSessionID)
                )
            elif isinstance(received_msg, GroupMsg):
                req_url = "http://d.web2.qq.com/channel/send_qun_msg2"
                data = (
                    ('r', '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(received_msg.from_uin, self.__operator.ClientID, received_msg.msg_id + 1, self.__operator.PSessionID, fix_content)),
                    ('clientid', self.__operator.ClientID),
                    ('psessionid', self.__operator.PSessionID)
                )
            rsp = HttpClient().Post(req_url, data, self.__operator.nowConfig.connect_referer)
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
            print "Reply response: " + str(rsp_json)
            return rsp_json
        except:
            if last_fail_times < 5:
                # loggin.error("Response Error.Wait for 2s and Retrying."+str(lastFailTimes))
                # logging.info(rsp)
                print "Response Error.Wait for 2s and Retrying." + str(last_fail_times)
                print rsp
                last_fail_times += 1
                time.sleep(2)
                self.reply_msg(received_msg, reply_content, last_fail_times + 1)
            else:
                print "Response Error over 5 times.Exit."
                # logging.error("Response Error over 5 times.Exit.")
                raise ValueError(rsp)
