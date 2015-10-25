#coding:utf-8
import urllib2
import json

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Turing:
    def getReply(self,info):
        # try:
            info=urllib2.quote(info.encode('utf-8'))
            # print info
            urlStr="http://www.tuling123.com/openapi/api?key=2bd2aeb49107f6e7499b8a4dee9a6cab&info=%s" % info
            response=urllib2.urlopen(urlStr)
            dataHtml=response.read()
            # print dataHtml
            data=json.loads(dataHtml)
            dir(data['code'])
            code=str(data['code'])
            if code =='100000':
                return strip_tags(data['text'])

            elif code =='200000':
                return u'你需要的信息在：'+data['url']

            elif code =='302000':
                return data['text']+" "+\
                data['list'][0]['article']+\
                u'更多:'+data['list'][0]['detailurl']

            elif code =='305000':
                return data['text']+" "+\
                data['list'][0]['trainnum']+\
                u' 始发站:'+data['list'][0]['start']+\
                u' 终点站:'+data['list'][0]['terminal']+\
                u' 发车时间:'+data['list'][0]['starttime']+\
                u' 到站时间:'+data['list'][0]['endtime']+\
                u' 更多:'+data['list'][0]['detailurl']
            elif str(code) =='308000':
                # str="%s %s %s %s" % data['text'], data['list'][0]['name'], data['list'][0]['info'], data['list'][0]['detailurl']
                str1= data['text']+" "+\
                data['list'][0]['name']+\
                ' '+data['list'][0]['info']+\
                u' 更多:' + data['list'][0]['detailurl']
                return str1
            else:
                return 'Not Found !'
        # except:
        #     return "None Found ！"

# Usage:
# tr=Turing()
# print tr.getReply('北京到拉萨的火车')
