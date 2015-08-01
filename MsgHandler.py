# -*- coding: utf-8 -*-

from Group import *
from Pm import *

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
                if msg.info_seq not in self.__group_list:
                    self.__group_list[msg.info_seq] = Group(self.__operator, msg)
                    self.__group_list[msg.info_seq].start()
                    logging.debug("Now group thread list:  " + str(self.__group_list))

                tgt_group = self.__group_list[msg.info_seq]
                if len(tgt_group.msg_list) >= 1 and msg.seq == tgt_group.msg_list[-1].seq:
                    # 若如上一条seq重复则抛弃此条信息不处理
                    logging.info("消息重复，抛弃")
                    return
                tgt_group.msg_id = msg.msg_id
                self.__group_list[msg.info_seq].handle(msg)
                tgt_group.msg_list.append(msg)

            elif isinstance(msg, PmMsg):
                tid = self.__operator.get_account(msg)
                if tid not in self.__pm_list:
                    self.__pm_list[tid] = Pm(self.__operator, msg)
                    self.__pm_list[tid].start()
                    logging.debug("Now pm thread list:  " + str(self.__pm_list))

                tgt_pm = self.__pm_list[tid]
                if len(tgt_pm.msg_list) >= 1 and msg.time == tgt_pm.msg_list[-1].time \
                        and msg.from_uin == tgt_pm.msg_list[-1].from_uin \
                        and msg.content == tgt_pm.msg_list[-1].content:
                    # 私聊没有seq可用于判断重复，只能抛弃同一个人在同一时间戳发出的内容相同的消息。
                    logging.info("消息重复，抛弃")
                    return
                tgt_pm.msg_id = msg.msg_id
                self.__pm_list[tid].handle(msg)
                tgt_pm.msg_list.append(msg)

            elif isinstance(msg, SessMsg):
                pass

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

    def reply_msg(self, received_msg, reply_content, fail_times=0):
        #TODO: 此方法将被遗弃
        last_fail_times = fail_times

        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode(
            "utf-8")
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
                    group_sig = json.loads(HttpClient().Get(
                        'http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={0}&to_uin={1}&clientid={2}&psessionid={3}&service_type={4}&t={5}'.format(
                            received_msg.id, received_msg.from_uin, self.__operator.client_id,
                            self.__operator.psessionid, received_msg.service_type, ts),
                        self.__operator.default_config.connect_referer))
                    if group_sig == "":
                        raise ValueError("Receive a None when getting group sig")
                except BaseException, e:
                    print "Getting group sig met an error: ", e
                req_url = "http://d.web2.qq.com/channel/send_sess_msg2"
                data = (
                    ('r',
                     '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}", "group_sig":"{5}", "service_type":{6}}}'.format(
                         received_msg.from_uin, self.__operator.client_id, received_msg.msg_id + 1,
                         self.__operator.psessionid, fix_content, group_sig, received_msg.service_type)),
                    ('clientid', self.__operator.client_id),
                    ('psessionid', self.__operator.psessionid),
                    ('group_sig', group_sig),
                    ('service_type', received_msg.service_type)
                )
            elif isinstance(received_msg, PmMsg):
                req_url = "http://d.web2.qq.com/channel/send_buddy_msg2"
                data = (
                    ('r',
                     '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(
                         received_msg.from_uin, self.__operator.client_id, received_msg.msg_id + 1,
                         self.__operator.psessionid, fix_content)),
                    ('clientid', self.__operator.client_id),
                    ('psessionid', self.__operator.psessionid)
                )
            elif isinstance(received_msg, GroupMsg):
                req_url = "http://d.web2.qq.com/channel/send_qun_msg2"
                data = (
                    ('r',
                     '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(
                         received_msg.from_uin, self.__operator.client_id, received_msg.msg_id + 1,
                         self.__operator.psessionid, fix_content)),
                    ('clientid', self.__operator.client_id),
                    ('psessionid', self.__operator.psessionid)
                )
            rsp = HttpClient().Post(req_url, data, self.__operator.default_config.connect_referer)
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
