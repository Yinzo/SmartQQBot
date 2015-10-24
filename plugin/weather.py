#coding:utf-8
import urllib2
import json

class Weather:
    def getWeatherOfCity(self,cityName):
        try:
            cityName=urllib2.quote(cityName)
            print cityName
            urlStr="http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=31662bc776555612e3639dbca1ad1fd5" % cityName
            response=urllib2.urlopen(urlStr)
            dataHtml=response.read()
            # print dataHtml
            data=json.loads(dataHtml)
            return data['results'][0]['currentCity']+\
            " pm:"+ data['results'][0]['pm25'] + \
            data['results'][0]['index'][0]['title']+":"+\
            data['results'][0]['index'][0]['zs']+" "+\
            data['results'][0]['index'][0]['des']+\
            data['results'][0]['weather_data'][0]['date']+":"+\
            data['results'][0]['weather_data'][0]['weather']+\
            data['results'][0]['weather_data'][0]['temperature']+\
            data['results'][0]['weather_data'][0]['wind']+\
            data['results'][0]['weather_data'][1]['date']+":"+\
            data['results'][0]['weather_data'][1]['weather']+" "+\
            data['results'][0]['weather_data'][1]['temperature']+" "+\
            data['results'][0]['weather_data'][1]['wind']+\
            data['results'][0]['weather_data'][2]['date']+":"+\
            data['results'][0]['weather_data'][2]['weather']+" "+\
            data['results'][0]['weather_data'][2]['temperature']+" "+\
            data['results'][0]['weather_data'][2]['wind']
            
        except:
            return "None found city"

# Usage:
# tq=Weather()
# print tq.getWeatherOfCity('上海')
