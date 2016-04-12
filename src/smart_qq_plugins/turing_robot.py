# coding: utf-8
from random import randint
import requests

from smart_qq_bot.signals import on_all_message

# 使用前请先前往 http://apistore.baidu.com/apiworks/servicedetail/736.html
# 申请 API 谢谢
# 另外需要 requests 支持
url = "http://apis.baidu.com/turing/turing/turing"
headers = {
    'apikey': "",
    'cache-control': "no-cache"
}


@on_all_message
def turing_robot(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.QMessage
    """

    querystring = {
        "key": "",
        "info": msg.content,
        "userid": ""
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    response_json = response.json()

    bot.send_qun_msg(msg.from_uin, response_json.get('text'), msg_id=randint(1, 1000))

    if msg.poll_type is 'group_message':
        bot.send_qun_msg(msg.from_uin, response_json.get('text'), msg_id=randint(1, 1000))
    else:
        bot.send_buddy_msg(msg.from_uin, response_json.get('text'), msg_id=randint(1, 1000))
