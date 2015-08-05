# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

class Notify:

    def __init__(self, json_input):
        self.poll_type = json_input['poll_type']


class InputNotify(Notify):

    def __init__(self, json_input):
        Notify.__init__(self, json_input)
        self.from_uin = json_input['value']['from_uin']
        self.msg_id = json_input['value']['msg_id']
        self.msg_id2 = json_input['value']['msg_id2']
        self.msg_type = json_input['value']['msg_type']
        self.reply_ip = json_input['value']['reply_ip']
        self.to_uin = json_input['value']['to_uin']


class BuddiesStatusChange(Notify):

    def __init__(self, json_input):
        Notify.__init__(self, json_input)
        self.status = json_input['value']['status']
        self.client_type = json_input['value']['client_type']
        self.uin = json_input['value']['uin']


class KickMessage(Notify):

        def __init__(self, json_input):
            Notify.__init__(self, json_input)
            self.reply_ip = json_input['value']['reply_ip']
            self.msg_type = json_input['value']['msg_type']
            self.msg_id = json_input['value']['msg_id']
            self.reason = json_input['value']['reason']
            self.msg_id2 = json_input['value']['msg_id2']
            self.from_uin = json_input['value']['from_uin']
            self.show_reason = json_input['value']['show_reason']
            self.to_uin = json_input['value']['to_uin']
