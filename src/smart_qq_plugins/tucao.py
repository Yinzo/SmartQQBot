# -*- coding: utf-8 -*-
import re
import os
import random
from six.moves import cPickle
import six

from smart_qq_bot.logger import logger
from smart_qq_bot.signals import (
    on_all_message,
    on_group_message,
)

TUCAO_PATH = 'smart_qq_plugins/tucao/'


class TucaoCore(object):

    def __init__(self):
        self.tucao_dict = dict()

    def save(self, group_id):
        """
        :type group_id: int, 用于保存指定群的吐槽存档
        """
        global TUCAO_PATH
        try:
            tucao_file_path = TUCAO_PATH + str(group_id) + ".tucao"
            with open(tucao_file_path, "w+") as tucao_file:
                cPickle.dump(self.tucao_dict[str(group_id)], tucao_file)
            logger.info("RUNTIMELOG tucao saved. Now tucao list:  {0}".format(str(self.tucao_dict)))
        except Exception:
            logger.error("RUNTIMELOG Fail to save tucao.")
            raise IOError("Fail to save tucao.")

    def load(self, group_id):
        """
        :type group_id: int, 用于读取指定群的吐槽存档
        """
        global TUCAO_PATH
        if str(group_id) in set(self.tucao_dict.keys()):
            return

        tucao_file_path = TUCAO_PATH + str(group_id) + ".tucao"
        if not os.path.isdir(TUCAO_PATH):
            os.makedirs(TUCAO_PATH)
        if not os.path.exists(tucao_file_path):
            with open(tucao_file_path, "w") as tmp:
                tmp.close()
        with open(tucao_file_path, "rb") as tucao_file:
            try:
                self.tucao_dict[str(group_id)] = cPickle.load(tucao_file)
                logger.info("RUNTIMELOG tucao loaded. Now tucao list:  {0}".format(str(self.tucao_dict)))
            except EOFError:
                self.tucao_dict[str(group_id)] = dict()
                logger.info("RUNTIMELOG tucao file is empty.")



core = TucaoCore()

@on_group_message(name='tucao[学习遗忘]')
def tucao(msg, bot):
    global core
    reply = bot.reply_msg(msg, return_function=True)
    group_code = str(msg.group_code)
    group_id = str(bot.get_group_info(group_code=group_code).get('id'))

    match = re.match(r'^(?:!|！)(learn|delete)(?:\s?){(.+)}(?:\s?){(.+)}', msg.content)
    if match:
        core.load(group_id)

        logger.info("RUNTIMELOG tucao command detected.")
        command = str(match.group(1)).decode('utf8')
        key = str(match.group(2)).decode('utf8')
        value = str(match.group(3)).decode('utf8')

        if command == 'learn':
            if group_id not in core.tucao_dict:
                core.load(group_id)
            if key in core.tucao_dict[group_id] and value not in core.tucao_dict[group_id][key]:
                core.tucao_dict[group_id][key].append(value)
            else:
                core.tucao_dict[group_id][key] = [value]
            reply("学习成功！快对我说" + str(key) + "试试吧！")
            core.save(group_id)
            return True

        elif command == 'delete':
            if key in core.tucao_dict[group_id] and core.tucao_dict[group_id][key].count(value):
                core.tucao_dict[group_id][key].remove(value)
                reply("呜呜呜我再也不说" + str(value) + "了")
                core.save(group_id)
                return True
    else:
        core.load(group_id)
        for key in list(core.tucao_dict[group_id].keys()):
            if str(key) in msg.content and core.tucao_dict[group_id][key]:
                logger.info("RUNTIMELOG tucao pattern detected, replying...")
                reply(random.choice(core.tucao_dict[group_id][key]))
                return True
    return False


@on_group_message(name='tucao[吐槽列表]')
def current_tucao_list(msg, bot):
    # webqq接受的消息会以空格结尾

    global core
    reply = bot.reply_msg(msg, return_function=True)
    group_code = str(msg.group_code)
    group_id = str(bot.get_group_info(group_code=group_code).get('id'))

    match = re.match(r'^(?:!|！)([^\s\{\}]+)\s*$', msg.content)
    if match:
        core.load(group_id)

        command = str(match.group(1))
        logger.info("RUNTIMELOG command format detected, command: " + command)

        if command == "吐槽列表":
            result = ""
            for key in list(core.tucao_dict[group_id].keys()):
                result += "关键字：{0}\t\t回复：{1}\n".format(key, " / ".join(core.tucao_dict[group_id][key]))
            result = result[:-1]
            logger.info("RUNTIMELOG Replying the list of tucao for group {}".format(group_id))
            reply(result)
    return


@on_group_message(name='tucao[删除关键字]')
def delete_tucao(msg, bot):
    global core
    reply = bot.reply_msg(msg, return_function=True)
    group_code = str(msg.group_code)
    group_id = str(bot.get_group_info(group_code=group_code).get('id'))

    match = re.match(r'^(?:!|！)([^\s\{\}]+)(?:\s?)\{([^\s\{\}]+)\}\s*$', msg.content)
    if match:
        core.load(group_id)

        command = str(match.group(1))
        arg1 = str(match.group(2))
        logger.info("RUNTIMELOG command format detected, command:{0}, arg1:{1}".format(command, arg1))
        if command == "删除关键字" and six.text_type(arg1) in core.tucao_dict[group_id]:
            core.tucao_dict[group_id].pop(
                six.text_type(arg1)
            )
            reply("已删除关键字:{0}".format(arg1))
            core.save(group_id)
            return True
    return False
