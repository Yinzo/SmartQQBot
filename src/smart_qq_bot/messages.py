# coding: utf-8

PRIVATE_MSG = "message"
GROUP_MSG = "group_message"
SESS_MSG = "sess_message"
INPUT_NOTIFY_MSG = "input_notify"
KICK_MSG = "kick_message"


class QMessage(object):

    def __init__(self, json_input):
        self.poll_type = json_input['poll_type']
        self.from_uin = json_input['value']['from_uin']
        self.msg_id = json_input['value']['msg_id']
        self.msg_type = json_input['value']['msg_type']
        self.to_uin = json_input['value']['to_uin']


class MsgWithContent(QMessage):

    def __init__(self, json_input):
        super(MsgWithContent, self).__init__(json_input)
        self.raw_content = json_input['value']['content']
        self.content = MsgWithContent.combine_msg(self.raw_content)
        for i in json_input['value']['content']:
            if isinstance(i, list) and i[0] == "font":
                self.font = i[1]
        self.time = json_input['value']['time']

    @staticmethod
    def combine_msg(content):
        msgtxt = ""
        for part in content:
            if type(part) == type(u'\u0000'):
                msgtxt += part
            elif len(part) > 1:
                # 如果是图片
                if str(part[0]) == "offpic":
                    msgtxt += "[图片]"
                elif str(part[0]) == "cface":
                    msgtxt += "[表情]"

        return msgtxt


# 临时会话消息
class SessMsg(MsgWithContent):

    def __init__(self, json_input):
        MsgWithContent.__init__(self, json_input)
        self.service_type = json_input['value']['service_type']
        self.id = json_input['value']['id']
        self.ruin = json_input['value']['ruin']
        self.flags = json_input['value']['flags']


class PmMsg(MsgWithContent):

    def __init__(self, json_input):
        MsgWithContent.__init__(self, json_input)


class GroupMsg(MsgWithContent):

    def __init__(self, json_input):
        MsgWithContent.__init__(self, json_input)
        self.group_code = json_input['value']['group_code']
        self.send_uin = json_input['value']['send_uin']