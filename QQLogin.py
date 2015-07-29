# -*- coding: utf-8 -*-
import random
import time
import datetime
import re
import json

from Configs import *
from Msg import *
from Notify import *
from HttpClient import *


def get_revalue(html, rex, er, ex):
    v = re.search(rex, html)

    if v is None:
        # logging.error(er)

        if ex:
            raise TypeError(er)
        else:
            print er
        return ''

    return v.group(1)


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000


class QQ:
    def __init__(self):
        self.nowConfig = DefaultConfigs()
        self.req = HttpClient()

        self.FriendList = {}

        self.ClientID = int(random.uniform(111111, 888888))
        self.PTWebQQ = ''
        self.PSessionID = ''
        self.APPID = 0
        self.VFWebQQ = 0
        self.msgId = 0
        self.VPath = self.nowConfig.conf.get("global", "qrcode_path")  # QRCode保存路径

    def login_by_qrcode(self):
        print "正在获取登陆页面"
        initurl = get_revalue(self.req.Get(self.nowConfig.conf.get("global", "smartqq_url")), r'\.src = "(.+?)"', "Get Login Url Error.", 1)
        html = self.req.Get(initurl + '0')

        print "正在获取appid"
        appid = get_revalue(html, r'var g_appid =encodeURIComponent\("(\d+)"\);', 'Get AppId Error', 1)

        print "正在获取login_sig"
        sign = get_revalue(html, r'var g_login_sig=encodeURIComponent\("(.+?)"\);', 'Get Login Sign Error', 0)

        print "正在获取pt_version"
        js_ver = get_revalue(html, r'var g_pt_version=encodeURIComponent\("(\d+)"\);', 'Get g_pt_version Error', 1)

        print "正在获取mibao_css"
        mibao_css = get_revalue(html, r'var g_mibao_css=encodeURIComponent\("(.+?)"\);', 'Get g_mibao_css Error', 1)

        star_time = date_to_millis(datetime.datetime.utcnow())

        error_times = 0
        ret = []
        while True:
            error_times += 1
            self.req.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(appid),
                              self.VPath)
            print "登陆二维码下载成功，请扫描"

            while True:
                html = self.req.Get(
                    'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(
                        appid, date_to_millis(datetime.datetime.utcnow()) - star_time, mibao_css, js_ver, sign), initurl)
                ret = html.split("'")
                if ret[1] == '65' or ret[1] == '0':  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                    break
                time.sleep(2)
            if ret[1] == '0' or error_times > 10:
                break

        if ret[1] != '0':
            return
        print "二维码已扫描，正在登陆"

        # 删除QRCode文件
        if os.path.exists(self.VPath):
            os.remove(self.VPath)

        # 记录登陆账号的昵称
        tmp_username = ret[11]

        html = self.req.Get(ret[5])
        url = get_revalue(html, r' src="(.+?)"', 'Get mibao_res Url Error.', 0)
        if url != '':
            html = self.req.Get(url.replace('&amp;', '&'))
            url = get_revalue(html, r'location\.href="(.+?)"', 'Get Redirect Url Error', 1)
            html = self.req.Get(url)

        self.PTWebQQ = self.req.getCookie('ptwebqq')

        login_error = 1
        ret = {}
        while login_error > 0:
            try:
                html = self.req.Post('http://d.web2.qq.com/channel/login2', {
                    'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.PTWebQQ,
                                                                                                          self.ClientID,
                                                                                                          self.PSessionID)
                }, self.nowConfig.conf.get("global", "connect_referer"))
                ret = json.loads(html)
                login_error = 0
            except:
                login_error += 1
                print "登录失败，正在重试"

        if ret['retcode'] != 0:
            print "return code:" + str(ret['retcode'])
            return

        self.VFWebQQ = ret['result']['vfwebqq']
        self.PSessionID = ret['result']['psessionid']

        print "QQ号：{0} 登陆成功, 用户名：{1}".format(ret['result']['uin'], tmp_username)
        self.msgId = int(random.uniform(20000, 50000))

    def check_msg(self):
        # 调用后进入单次轮询，等待服务器发回状态。
        html = self.req.Post('http://d.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(self.PSessionID, self.PTWebQQ,
                                                                                         self.ClientID)
        }, self.nowConfig.conf.get("global", "connect_referer"))
        try:
            if html == "":
                return self.check_msg()
            ret = json.loads(html)

            ret_code = ret['retcode']

            if ret_code in (102, ):
                print "received retcode: " + str(ret_code) + ": No message."
                return

            if ret_code in (121, ):
                print "received retcode: " + str(ret_code)
                raise KeyError("Account offline.")

            elif ret_code == 0:
                msg_list = []
                for msg in ret['result']:
                    ret_type = msg['poll_type']
                    if ret_type == 'message':
                        msg_list.append(PmMsg(msg))
                    elif ret_type == 'group_message':
                        msg_list.append(GroupMsg(msg))
                    elif ret_type == 'sess_message':
                        msg_list.append(SessMsg(msg))
                    elif ret_type == 'input_notify':
                        msg_list.append(InputNotify(msg))
                    elif ret_code == 'kick_message':
                        msg_list.append(KickMessage(msg))
                    else:
                        print "unknown message type: " + str(ret_type)
                        print msg
                if not msg_list:
                    return
                return msg_list

            elif ret_code == 100006:
                print "POST data error"
                return

            elif ret_code == 116:
                self.PTWebQQ = ret['p']
                print "PTWebQQ has been updated."
                return

            else:
                print "unknown retcode " + str(ret_code)
                return

        except ValueError, e:
            print "Check error occured: " + str(e)
            # print "received HTML: " + str(html)
        except BaseException, e:
            print "Check error occured, retrying. Error: " + str(e)
            return self.check_msg()

    # 查询QQ号，通常首次用时0.2s，以后基本不耗时
    def get_account(self, msg):
        assert isinstance(msg, (Msg, Notify)), "function get_account received a not Msg or Notify parameter."

        if isinstance(msg, (PmMsg, SessMsg, InputNotify)):
            # 如果消息的发送者的真实QQ号码不在FriendList中,则自动去取得真实的QQ号码并保存到缓存中
            tuin = msg.from_uin
            account = self.uin_to_account(tuin)
            return account

        elif isinstance(msg, GroupMsg):
            return str(msg.info_seq).join("[]") + str(self.uin_to_account(msg.send_uin))

    def uin_to_account(self, tuin):
        uin_str = str(tuin)
        if uin_str not in self.FriendList:
            try:
                info = json.loads(HttpClient().Get(
                    'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}'.format(uin_str, self.VFWebQQ),
                    self.nowConfig.conf.get("global", "connect_referer")))
                # logging.info("Get uin to account info:" + str(info))
                if info['retcode'] != 0:
                    print info
                    raise TypeError('uin to account result error')
                info = info['result']
                self.FriendList[uin_str] = info['account']

            except BaseException, error:
                # logging.error(e)
                print error

        assert isinstance(uin_str, str), "tuin is not string"
        try:

            return self.FriendList[uin_str]
        except KeyError, e:
            print e
            print list(self.FriendList)
