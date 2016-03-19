# coding: utf-8

PRIVATE_MSG = "message"
GROUP_MSG = "group_message"
SESS_MSG = "sess_message"
INPUT_NOTIFY_MSG = "input_notify"
KICK_MSG = "kick_message"

# Msg type in message content
OFF_PIC_PART = "offpic"
C_FACE_PART = "cface"

OFF_PIC_PLACEHOLDER = "[图片]"
C_FACE_PLACEHOLDER = "[表情]"


def mk_msg(msg_dict):
    msg_map = {
        GROUP_MSG: GroupMsg,
        INPUT_NOTIFY_MSG: QMessage,
        KICK_MSG: QMessage,
        SESS_MSG: SessMsg,
        PRIVATE_MSG: PrivateMsg,
    }
    return msg_map[msg_dict['pool_type']]


class QMessage(object):

    def __init__(self, msg_dict):
        self.meta = msg_dict

        self.poll_type = msg_dict['poll_type']
        value = msg_dict['value']

        self.from_uin = value['from_uin']
        self.msg_id = value['msg_id']
        self.msg_type = value['msg_type']
        self.to_uin = value['to_uin']
        self._content = value['content']
        self.time = value['time']
        self.font = None

        for i in value['content']:
            if isinstance(i, list) and i[0] == "font":
                self.font = i[1]

    @property
    def content(self):
        text = ""
        for msg_part in self._content:
            if isinstance(msg_part, basestring):
                text += msg_part
            elif len(msg_part) > 1:
                if str(msg_part[0]) == "offpic":
                    text += ""
                elif str(text[0]) == "cface":
                    text += "[表情]"

        return text


class SessMsg(QMessage):
    """
    临时会话消息
    """

    def __init__(self, msg_dict):
        super(SessMsg, self).__init__(msg_dict)
        self.service_type = msg_dict['value']['service_type']
        self.id = msg_dict['value']['id']
        self.ruin = msg_dict['value']['ruin']
        self.flags = msg_dict['value']['flags']


class PrivateMsg(QMessage):
    pass


class GroupMsg(QMessage):

    def __init__(self, msg_dict):
        super(GroupMsg, self).__init__(msg_dict)
        self.group_code = msg_dict['value']['group_code']
        self.send_uin = msg_dict['value']['send_uin']