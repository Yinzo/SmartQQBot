# -*- coding: utf-8 -*-

from HttpClient import HttpClient
import re, random, md5, json, os, sys, datetime, time, threading, subprocess, logging

reload(sys)
sys.setdefaultencoding("utf-8")

HttpClient_Ist = HttpClient()

ClientID = int(random.uniform(111111, 888888))
PTWebQQ = ''
APPID = 0
msgId = 0
FriendList = {}
PSessionID = ''
Referer = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
SmartQQUrl = 'http://w.qq.com/login.html'
VFWebQQ = ''
AdminQQ = '0'

# -----------------
# 方法声明
# -----------------

def getReValue(html, rex, er, ex):
	v = re.search(rex, html)
	#如果匹配失败
	if v is None:

		#记录错误
		logging.error(er)

		#如果条件成立,则抛异常
		if ex:
			raise Exception, er

		return ''


	return v.group(1)#返回匹配到的内容


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000


def uin_to_account(tuin):
	#如果消息的发送者的真实QQ号码不在FriendList中,则自动去取得真实的QQ号码并保存到缓存中
	if not tuin in FriendList:
		try:
			info = json.loads(HttpClient_Ist.Get('http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}'.format(tuin, VFWebQQ), Referer))
			logging.info(info)
			if info['retcode'] != 0:
				raise ValueError, info
			info = info['result']
			FriendList[tuin] = info['account']

		except Exception as e:
			logging.debug(e)

	logging.info(FriendList)
	return FriendList[tuin]

def msg_handler(msgObj):
	for msg in msgObj:
		msgType = msg['poll_type']

	#QQ私聊消息
	if msgType == 'message':
		txt = combine_msg(msg['value']['content'])
		logging.debug(txt)
		tuin = msg['value']['from_uin']
		from_account = uin_to_account(tuin)

		print "{0}:{1}".format(from_account,txt)

		send_msg(tuin,"huehuehue")
		# print "{0}:{1}".format(self.FriendList.get(tuin, 0),txt)


		# if FriendList.get(tuin, 0) == AdminQQ:#如果消息的发送者与AdminQQ不相同,则忽略本条消息不往下继续执行
		# 	if txt[0] == '#':
		# 		thread.start_new_thread(self.runCommand, (tuin, txt[1:].strip(), msgId))
		# 		msgId += 1

		# if txt[0:4] == 'exit':
		# 	logging.info(self.Get('http://d.web2.qq.com/channel/logout2?ids=&clientid={0}&psessionid={1}'.format(self.ClientID, self.PSessionID), Referer))
		# 	exit(0)

	#群消息
	elif msgType == 'group_message': 
		txt = combine_msg(msg['value']['content'])
		logging.debug(txt)

		tuin = msg['value']['from_uin']
		from_account = uin_to_account(tuin)

		print "{0}:{1}".format(from_account,txt)
		

	#QQ号在另一个地方登陆,被挤下线
	elif msgType == 'kick_message':
		logging.error(msg['value']['reason'])
		raise Exception, msg['value']['reason']#抛出异常,重新启动WebQQ,需重新扫描QRCode来完成登陆


def combine_msg(content):
	msgTXT = ""
	for part in content:
		# print type(part)
		if type(part) == type(u'\u0000'):
			msgTXT += part
		elif len(part) > 1:
			if part[0] == "offpic":
				msgTXT += "[图片]"

	return msgTXT

def send_msg(tuin,content):
	reqURL = "http://d.web2.qq.com/channel/send_buddy_msg2"
	data = (
		('r', '{{"to":{0},"face":594,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(tuin, ClientID, msgId, PSessionID, content)),
		('clientid', ClientID),
		('psessionid', PSessionID)
	)
	rsp = HttpClient_Ist.Post(reqURL,data,Referer)

	return rsp

# -----------------
# 类声明
# -----------------

class Login(HttpClient):
	MaxTryTime = 5


	def __init__(self,vpath, qq=0):
		global APPID,AdminQQ,PTWebQQ,VFWebQQ,PSessionID,msgId
		self.VPath = vpath#QRCode保存路径
		AdminQQ = int(qq)
		logging.basicConfig(filename='qq.log', level=logging.DEBUG, format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
		print "正在获取登陆页面"
		self.initUrl = getReValue(self.Get(SmartQQUrl), r'\.src = "(.+?)"', 'Get Login Url Error.', 1)
		html = self.Get(self.initUrl + '0')

		print "正在获取appid"
		APPID = getReValue(html, r'var g_appid =encodeURIComponent\("(\d+)"\);', 'Get AppId Error', 1)
		print "正在获取login_sig"
		sign = getReValue(html, r'var g_login_sig=encodeURIComponent\("(.+?)"\);', 'Get Login Sign Error', 1)
		logging.info('get sign : %s', sign)
		print "正在获取pt_version"
		JsVer = getReValue(html, r'var g_pt_version=encodeURIComponent\("(\d+)"\);', 'Get g_pt_version Error', 1)
		logging.info('get g_pt_version : %s', JsVer)
		print "正在获取mibao_css"
		MiBaoCss = getReValue(html, r'var g_mibao_css=encodeURIComponent\("(.+?)"\);', 'Get g_mibao_css Error', 1)
		logging.info('get g_mibao_css : %s', sign)
		StarTime = date_to_millis(datetime.datetime.utcnow())

		T = 0
		while True:
			T = T + 1
			self.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(APPID), self.VPath)
			print "登陆二维码下载成功，请扫描"
			logging.info('[{0}] Get QRCode Picture Success.'.format(T))


			while True:
				html = self.Get('https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(APPID, date_to_millis(datetime.datetime.utcnow()) - StarTime, MiBaoCss, JsVer, sign), self.initUrl)
				#logging.info(html)
				ret = html.split("'")
				if ret[1] == '65' or ret[1] == '0':#65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
					break
				time.sleep(2)
			if ret[1] == '0' or T > self.MaxTryTime:
				break

		logging.debug(ret)
		if ret[1] != '0':
			return
		print "二维码已扫描，正在登陆"

		#删除QRCode文件
		if os.path.exists(self.VPath):
			os.remove(self.VPath)

		#记录登陆账号的昵称
		tmpUserName = ret[11]


		html = self.Get(ret[5])
		url = getReValue(html, r' src="(.+?)"', 'Get mibao_res Url Error.', 0)
		if url != '':
			html = self.Get(url.replace('&amp;', '&'))
			url = getReValue(html, r'location\.href="(.+?)"', 'Get Redirect Url Error', 1)
			html = self.Get(url)

		PTWebQQ = self.getCookie('ptwebqq')

		logging.info('PTWebQQ: {0}'.format(PTWebQQ))
		html = self.Post('http://d.web2.qq.com/channel/login2', {
			'r' : '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(PTWebQQ, ClientID, PSessionID)
		}, Referer)

		logging.debug(html)
		ret = json.loads(html)

		if ret['retcode'] != 0:
			return

		VFWebQQ = ret['result']['vfwebqq']
		PSessionID = ret['result']['psessionid']

		print "QQ号：{0} 登陆成功,用户名：{1}".format(ret['result']['uin'],tmpUserName)
		logging.info('Login success')

		msgId = int(random.uniform(20000, 50000))

class check_msg(threading.Thread):
	# try:
	#   pass
	# except KeybordInterrupt:
	#   try:
	#     user_input = (raw_input("回复系统：（输入格式:{群聊2or私聊1},{群号or账号},{内容}）\n")).split(",")
	#     if (user_input[0] == 1):

	#       for kv in self.FriendList :
	#         if str(kv[1]) == str(user_input[1]):
	#           tuin == kv[0]

	#       self.send_msg(tuin,user_input[2])

	#   except KeybordInterrupt:
	#     exit(0)
	#   except Exception,e:
	#     print Exception,e

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global PTWebQQ

		E = 0


		#心跳包轮询
		while 1: 
			if E > 5:
				break
			ret = self.check()
			

			#POST数据有误
			if ret['retcode'] == 100006:
				break

			#返回数据有误
			if ret == "":
				E += 1
				continue

			#无消息
			if ret['retcode'] == 102:
				continue

			#更新PTWebQQ值
			if ret['retcode'] == 116:
				PTWebQQ = ret['p']
				continue

			#收到消息
			if ret['retcode'] == 0:
				#信息分发
				msg_handler(ret['result'])
				continue

	def check(self):
		html = HttpClient_Ist.Post('http://d.web2.qq.com/channel/poll2', {
			'r' : '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(PSessionID, PTWebQQ, ClientID)
		}, Referer)

		logging.info(html)

		try:
			ret = json.loads(html)
		except Exception as e:
			logging.debug(e)
			return ""
		return ret

# -----------------
# 主程序
# -----------------

if __name__ == "__main__":
	vpath = './v.jpg'
	qq = 0
	if len(sys.argv) > 1:
		vpath = sys.argv[1]
	if len(sys.argv) > 2:
		qq = sys.argv[2]

	try:
		qqLogin = Login(vpath, qq)
	except Exception, e:
		print e,Exception

	t_check = check_msg()
	t_check.setDaemon(True)
	t_check.start()

	while 1:
		if not t_check.isAlive():
			exit(0)
		time.sleep(1)



