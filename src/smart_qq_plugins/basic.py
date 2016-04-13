# -*- coding: utf-8 -*-
import logging

from smart_qq_bot.signals import (
    on_all_message,
    on_group_message,
    on_private_message,
)

@on_all_message(name='callout')
def callout(msg, bot):
    if "智障机器人" in msg.content:
        logging.info("RUNTIMELOG " + str(msg.gounp_code) + " calling me out, trying to reply....")
        bot.reply_msg(msg, "干嘛（‘·д·）")



class Recorder(object):

    def __init__(self):
        self.msg_list = list()

recorder = Recorder()
@on_group_message(name='repeat')
def repeat(msg, bot):
    global recorder
    if len(recorder.msg_list) > 0 and recorder.msg_list[-1].content == msg.content:
        if str(msg.content).strip() not in ("", " ", "[图片]", "[表情]"):
            logging.info("RUNTIMELOG " + str(msg.group_code) + " repeating, trying to reply " + str(msg.content))
            bot.reply_msg(msg, msg.content)
    recorder.msg_list.append(msg)
