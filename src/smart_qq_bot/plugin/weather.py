# coding:utf-8
import urllib2
import json


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


# Usage:
# tq=Weather()
# print tq.getWeatherOfCity('上海')
if __name__ == "__main__":
    query = Weather()
    info = query.getWeatherOfCity(u'深圳')
    print(info)
