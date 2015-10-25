# coding:utf-8
import json
import urllib2


class Wether:
    """docstring for  Wether"""

    def getWetherOfCity(self, city):
        # 构建查询天气的url
        url_str = "http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=A72e372de05e63c8740b2622d0ed8ab1" % city
        response = urllib2.urlopen(url_str)
        html = response.read()  # 获得天气数据
        # print html
        data = json.loads(html)
        str_data = ""
        try:

            print "city:", data['results'][0]['currentCity']
            print data['results'][0]["index"][0]['des']

            # print data['results'][0]["weather_data"][0]['date']
            # print data['results'][0]["weather_data"][0]['weather']
            # print data['results'][0]["weather_data"][0]['wind']
            # print data['results'][0]["weather_data"][0]['temperature']

            # print data['results'][0]["weather_data"][1]['date']
            # print data['results'][0]["weather_data"][1]['weather']
            # print data['results'][0]["weather_data"][1]['wind']
            # print data['results'][0]["weather_data"][1]['temperature']

            # print data['results'][0]["weather_data"][2]['date']
            # print data['results'][0]["weather_data"][2]['weather']
            # print data['results'][0]["weather_data"][2]['wind']
            # print data['results'][0]["weather_data"][2]['temperature']

            # print data['results'][0]["weather_data"][3]['date']
            # print data['results'][0]["weather_data"][3]['weather']
            # print data['results'][0]["weather_data"][3]['wind']
            # print data['results'][0]["weather_data"][3]['temperature']
            # print "city:", data['results'][0]['currentCity']
            # print data['results'][0]["index"][0]['des']

            str_data += "city:" + data['results'][0]['currentCity'] + "\n"
            str_data += data['results'][0]["index"][0]['des'] + "\n"

            str_data += data['results'][0]["weather_data"][0]['date'] + " "
            str_data += data['results'][0]["weather_data"][0]['weather'] + " "
            str_data += data['results'][0]["weather_data"][0]['wind'] + " "
            str_data += data['results'][0]["weather_data"][0]['temperature'] + " "

            str_data += data['results'][0]["weather_data"][1]['date'] + " "
            str_data += data['results'][0]["weather_data"][1]['weather'] + " "
            str_data += data['results'][0]["weather_data"][1]['wind'] + " "
            str_data += data['results'][0]["weather_data"][1]['temperature']

            str_data += data['results'][0]["weather_data"][2]['date'] + " "
            str_data += data['results'][0]["weather_data"][2]['weather'] + " "
            str_data += data['results'][0]["weather_data"][2]['wind'] + " "
            str_data += data['results'][0]["weather_data"][2]['temperature'] + " "

            str_data += data['results'][0]["weather_data"][3]['date'] + " "
            str_data += data['results'][0]["weather_data"][3]['weather'] + " "
            str_data += data['results'][0]["weather_data"][3]['wind'] + " "
            str_data += data['results'][0]["weather_data"][3]['temperature'] + " "
        except Exception, e:
            str_data = "city not found! "
        return str_data

# query = Wether()
# print query.getWetherOfCity("beijing")
# print query.getWetherOfCity("shanghai")
