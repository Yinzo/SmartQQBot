# coding:utf-8
import urllib2
import json
import re
import logging

from smart_qq_bot.signals import on_all_message

# Code by: john123951 / john123951@126.com

class Weather:
    def __init__(self):
        self.ak = '31662bc776555612e3639dbca1ad1fd5'

    def getWeatherOfCity(self, cityName):
        try:
            cityName = urllib2.quote(cityName.encode('utf-8'))
            urlStr = "http://api.map.baidu.com/telematics/v3/weather?location=%s&ak=%s&output=json" % (
                cityName, self.ak)
            response = urllib2.urlopen(urlStr)
            dataHtml = response.read()
            jsonResult = json.loads(dataHtml)['results'][0]

            str_data = ""
            str_data += jsonResult['currentCity'] + " PM:" + jsonResult['pm25'] + "\n"
            str_data += jsonResult["index"][0]['des'] + "\n"

            for data in jsonResult["weather_data"]:
                str_data += data['date'] + " "
                str_data += data['weather'] + " "
                str_data += data['wind'] + " "
                str_data += data['temperature']
                str_data += '\n'
            return str_data
        except:
            return "None found city"

query = Weather()

@on_all_message(name='weather')
def weather(msg, bot):
    global query

    match = re.match(ur'^(weather|天气) (\w+|[\u4e00-\u9fa5]+)', msg.content)
    if match:
        logging.info("RUNTIMELOG 查询天气...")
        command = match.group(1)
        city = match.group(2)
        logging.info("RUNTIMELOG 查询天气语句: " + msg.content)
        if command == 'weather' or command == u'天气':
            info = query.getWeatherOfCity(city)
            logging.info("RESPONSE " + str(info))
            bot.reply_msg(msg, str(info))
            return True
    return False

# Usage:
# tq=Weather()
# print tq.getWeatherOfCity('上海')
