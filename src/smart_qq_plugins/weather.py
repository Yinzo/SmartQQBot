# coding:utf-8

import json
import re

import six
from six.moves.urllib import (
    request,
    error,
    parse,
)

from smart_qq_bot.logger import logger
from smart_qq_bot.signals import on_all_message

# Code by:      john123951  /   john123951@126.com
# Modify by:    Yinzo       /   yinz995-1@yahoo.com

KEY = '31662bc776555612e3639dbca1ad1fd5'


@on_all_message(name='weather[天气查询]')
def weather(msg, bot):
    global query

    match = re.match(
        six.text_type('^(weather|天气) (.*)'),
        msg.content
    )
    if match:
        logger.info("RUNTIMELOG 查询天气...")
        command = match.group(1)
        city = match.group(2)
        logger.info("RUNTIMELOG 查询天气语句: " + msg.content)
        if command == 'weather' or command == six.text_type('天气'):
            try:
                city_name = parse.quote(city.encode('utf-8'))
                url_str = "http://api.map.baidu.com/telematics/v3/weather?location={city}&ak={key}&output=json".format(
                    city=city_name,
                    key=KEY
                )
                response = request.urlopen(url_str)
                data_html = response.read()
                logger.debug("RESPONSE {}".format(data_html))
                json_result = json.loads(data_html.decode('utf-8'))['results'][0]

                str_data = ""
                str_data += json_result['currentCity'] + " PM:" + json_result['pm25'] + "\n"
                try:
                    str_data += json_result["index"][0]['des'] + "\n"
                except:
                    pass

                for data in json_result["weather_data"]:
                    str_data += data['date'] + " "
                    str_data += data['weather'] + " "
                    str_data += data['wind'] + " "
                    str_data += data['temperature']
                    str_data += '\n'
            except Exception as ex:
                logger.debug(ex)
                str_data = "City not found :("

            bot.reply_msg(msg, str_data)
            return True
    return False
