# coding: utf-8
import six


PRIVATE_MSG = "message"
GROUP_MSG = "group_message"
SESS_MSG = "sess_message"
INPUT_NOTIFY_MSG = "input_notify"
KICK_MSG = "kick_message"
DISCUSS_MSG = "discu_message"

# Msg type in message content
OFF_PIC_PART = "offpic"
C_FACE_PART = "cface"

OFF_PIC_PLACEHOLDER = "[图片]"
C_FACE_PLACEHOLDER = "[表情]"


class QMessage(object):

    def __init__(self, msg_dict, bot_instance):
        self.bot = bot_instance
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
            if isinstance(msg_part, six.string_types):
                text += msg_part
            elif len(msg_part) > 1:
                if str(msg_part[0]) == OFF_PIC_PART:
                    text += OFF_PIC_PLACEHOLDER
                elif str(msg_part[0]) == C_FACE_PART:
                    text += C_FACE_PLACEHOLDER

        return text

    @property
    def type(self):
        return self.poll_type

    def __str__(self):
        return "<class {cls}: {content}>".format(
            cls=self.__class__.__name__,
            content=self.poll_type + " " + six.text_type(self._content)
        )

    def __unicode__(self):
        return six.text_type(self.__str__())


class SessMsg(QMessage):
    """
    临时会话消息
    """

    def __init__(self, msg_dict, bot_instance):
        super(SessMsg, self).__init__(msg_dict, bot_instance)
        self.service_type = msg_dict['value']['service_type']
        self.id = msg_dict['value']['id']
        self.ruin = msg_dict['value']['ruin']
        self.flags = msg_dict['value']['flags']


class PrivateMsg(QMessage):
    def __init__(self, msg_dict, bot_instance):
        super(PrivateMsg, self).__init__(msg_dict, bot_instance)
        self.to_uin = msg_dict['value']['to_uin']
        self.from_uin = msg_dict['value']['from_uin']


class GroupMsg(QMessage):

    def __init__(self, msg_dict, bot_instance):
        super(GroupMsg, self).__init__(msg_dict, bot_instance)
        self.group_code = msg_dict['value']['group_code']
        self.send_uin = msg_dict['value']['send_uin']
        self.from_uin = msg_dict['value']['from_uin']

    @property
    def src_group_name(self):
        info = self.bot.get_group_info(str(self.group_code))
        group_name = info.get('name')
        return group_name

    @property
    def src_group_id(self):
        info = self.bot.get_group_info(str(self.group_code))
        group_id = info.get('id')
        return group_id

    @property
    def src_sender_card(self):
        """
        获取发送者群名片
        """
        info = self.bot.get_group_member_info(str(self.group_code), self.send_uin)
        card = info.get('card')
        return card

    @property
    def src_sender_name(self):
        """
        获取发送者昵称
        """
        info = self.bot.get_group_member_info(str(self.group_code), self.send_uin)
        name = info.get('nick')
        return name

    @property
    def src_sender_id(self):
        """
        获取发送者真实QQ号
        """
        result_list = []
        member_list = self.bot.search_group_members(self.src_group_id)
        target_info = self.bot.get_group_member_info(str(self.group_code), self.send_uin)
        for info in member_list:
            if info.get('nick') == target_info.get('nick'):
                if info.get('card') and target_info.get('card'):
                    if info.get('card') == target_info.get('card'):
                        result_list.append(str(info.get('uin')))
                    else:
                        break
                else:
                    result_list.append(str(info.get('uin')))
        if len(result_list) > 1:
            raise IndexError('群内含有同名账号,获取真实QQ号失败')
        if len(result_list) == 0:
            return ""
        return result_list[0]

class DiscussMsg(QMessage):
    """
    讨论组消息
    """
    def __init__(self, msg_dict, bot_instance):
        super(DiscussMsg, self).__init__(msg_dict, bot_instance)
        self.did = msg_dict['value']['did']
        self.send_uin = msg_dict['value']['send_uin']
        self.from_uin = msg_dict['value']['from_uin']

    @property
    def src_discuss_name(self):
        info = self.bot.get_discuss_info(str(self.did))
        discuss_name = info.get('info').get('discu_name')
        return discuss_name or '未命名讨论组'

    @property
    def src_sender_name(self):
        info = self.bot.get_discuss_member_info(str(self.did), self.send_uin)
        name = info.get('nick')
        return name

    @property
    def src_sender_id(self):
        raise NotImplementedError("SmartQQ协议暂不支持查询讨论组消息发送者QQ号")

MSG_TYPE_MAP = {
    GROUP_MSG: GroupMsg,
    INPUT_NOTIFY_MSG: QMessage,
    KICK_MSG: QMessage,
    SESS_MSG: SessMsg,
    PRIVATE_MSG: PrivateMsg,
    DISCUSS_MSG: DiscussMsg,
}

def mk_msg(msg_dict, bot_instance):
    return MSG_TYPE_MAP[msg_dict['poll_type']](msg_dict, bot_instance)