# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import random
import time
import datetime
import re
import json
import logging

from Configs import *
from Msg import *
from Notify import *
from HttpClient import *

logging.basicConfig(
    filename='smartqq.log',
    level=logging.DEBUG,
    format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


def get_revalue(html, rex, er, ex):
    v = re.search(rex, html)

    if v is None:

        if ex:
            logging.error(er)
            raise TypeError(er)
        else:
            logging.warning(er)
        return ''

    return v.group(1)


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000


class QQ:
    def __init__(self):
        self.default_config = DefaultConfigs()
        self.req = HttpClient()

        self.friend_list = {}

        self.client_id = int(random.uniform(111111, 888888))
        self.ptwebqq = ''
        self.psessionid = ''
        self.appid = 0
        self.vfwebqq = ''
        self.qrcode_path = self.default_config.conf.get("global", "qrcode_path")  # QRCode保存路径
        self.username = ''
        self.account = 0

    def login_by_qrcode(self):
        logging.info("Requesting the login pages...")
        initurl_html = self.req.Get(self.default_config.conf.get("global", "smartqq_url"))
        logging.debug("login page html: " + str(initurl_html))
        initurl = get_revalue(initurl_html, r'\.src = "(.+?)"', "Get Login Url Error.", 1)
        html = self.req.Get(initurl + '0')

        appid = get_revalue(html, r'var g_appid =encodeURIComponent\("(\d+)"\);', 'Get AppId Error', 1)
        sign = get_revalue(html, r'var g_login_sig=encodeURIComponent\("(.+?)"\);', 'Get Login Sign Error', 0)
        js_ver = get_revalue(html, r'var g_pt_version=encodeURIComponent\("(\d+)"\);', 'Get g_pt_version Error', 1)
        mibao_css = get_revalue(html, r'var g_mibao_css=encodeURIComponent\("(.+?)"\);', 'Get g_mibao_css Error', 1)

        star_time = date_to_millis(datetime.datetime.utcnow())

        error_times = 0
        ret = []
        while True:
            error_times += 1
            self.req.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(appid),
                              self.qrcode_path)
            logging.info("Please scan the downloaded QRCode")

            while True:
                html = self.req.Get(
                    'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(
                        appid, date_to_millis(datetime.datetime.utcnow()) - star_time, mibao_css, js_ver, sign),
                    initurl)
                logging.debug("QRCode check html:   " + str(html))
                ret = html.split("'")
                if ret[1] in ('0', '65'):  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                    break
            if ret[1] == '0' or error_times > 10:
                break

        if ret[1] != '0':
            return
        logging.info("QRCode scaned, now logging in.")

        # 删除QRCode文件
        if os.path.exists(self.qrcode_path):
            os.remove(self.qrcode_path)

        # 记录登陆账号的昵称
        self.username = ret[11]

        html = self.req.Get(ret[5])
        logging.debug("mibao_res html:  " + str(html))
        url = get_revalue(html, r' src="(.+?)"', 'Get mibao_res Url Error.', 0)
        if url != '':
            html = self.req.Get(url.replace('&amp;', '&'))
            url = get_revalue(html, r'location\.href="(.+?)"', 'Get Redirect Url Error', 1)
            self.req.Get(url)

        self.ptwebqq = self.req.getCookie('ptwebqq')

        login_error = 1
        ret = {}
        while login_error > 0:
            try:
                html = self.req.Post('http://d.web2.qq.com/channel/login2', {
                    'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.ptwebqq,
                                                                                                          self.client_id,
                                                                                                          self.psessionid)
                }, self.default_config.conf.get("global", "connect_referer"))
                logging.debug("login html:  " + str(html))
                ret = json.loads(html)
                login_error = 0
            except:
                login_error += 1
                logging.info("login fail, retryng...")

        if ret['retcode'] != 0:
            logging.debug(str(ret))
            logging.warning("return code:" + str(ret['retcode']))
            return

        self.vfwebqq = ret['result']['vfwebqq']
        self.psessionid = ret['result']['psessionid']
        self.account = ret['result']['uin']

        logging.info("QQ：{0} login successfully, Username：{1}".format(self.account, self.username))

    def relogin(self, error_times=0):
        if error_times >= 10:
            return False
        try:
            html = self.req.Post('http://d.web2.qq.com/channel/login2', {
                'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","key":"","status":"online"}}'.format(
                    self.ptwebqq,
                    self.client_id,
                    self.psessionid)
            }, self.default_config.conf.get("global", "connect_referer"))
            logging.debug("relogin html:  " + str(html))
            ret = json.loads(html)
            self.vfwebqq = ret['result']['vfwebqq']
            self.psessionid = ret['result']['psessionid']
            return True
        except:
            logging.info("login fail, retryng..." + str(error_times))
            return self.relogin(error_times + 1)

    def check_msg(self, error_times=0):
        if error_times >= 5:
            if not self.relogin():
                raise IOError("Account offline.")
            else:
                error_times = 0

        # 调用后进入单次轮询，等待服务器发回状态。
        html = self.req.Post('http://d.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(self.psessionid, self.ptwebqq,
                                                                                         self.client_id)
        }, self.default_config.conf.get("global", "connect_referer"))
        logging.debug("check_msg html:  " + str(html))
        try:
            if html == "":
                return self.check_msg()
            ret = json.loads(html)

            ret_code = ret['retcode']

            if ret_code in (102,):
                logging.info("received retcode: " + str(ret_code) + ": No message.")
                time.sleep(1)
                return

            if ret_code in (103,):
                logging.warning("received retcode: " + str(ret_code) + ": Check error.retrying.." + str(error_times))
                return self.check_msg(error_times + 1)

            if ret_code in (121,):
                logging.warning("received retcode: " + str(ret_code))
                return self.check_msg(5)

            elif ret_code == 0:
                msg_list = []
                pm_list = []
                sess_list = []
                group_list = []
                notify_list = []
                for msg in ret['result']:
                    ret_type = msg['poll_type']
                    if ret_type == 'message':
                        pm_list.append(PmMsg(msg))
                    elif ret_type == 'group_message':
                        group_list.append(GroupMsg(msg))
                    elif ret_type == 'sess_message':
                        sess_list.append(SessMsg(msg))
                    elif ret_type == 'input_notify':
                        notify_list.append(InputNotify(msg))
                    elif ret_code == 'kick_message':
                        notify_list.append(KickMessage(msg))
                    else:
                        logging.warning("unknown message type: " + str(ret_type) + "details:    " + str(msg))

                group_list.sort(key=lambda x: x.seq)
                msg_list += pm_list + sess_list + group_list + notify_list
                if not msg_list:
                    return
                return msg_list

            elif ret_code == 100006:
                logging.warning("POST data error")
                return

            elif ret_code == 116:
                self.ptwebqq = ret['p']
                logging.info("ptwebqq updated.")
                return

            else:
                logging.warning("unknown retcode " + str(ret_code))
                return

        except ValueError, e:
            logging.warning("Check error occured: " + str(e))
            return self.check_msg(error_times + 1)

        except BaseException, e:
            logging.warning("Unknown check error occured, retrying. Error: " + str(e))
            return self.check_msg(error_times + 1)

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
        if uin_str not in self.friend_list:
            try:
                logging.info("Requesting the account by uin:    " + str(tuin))
                info = json.loads(HttpClient().Get(
                    'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}'.format(uin_str,
                                                                                                  self.vfwebqq),
                    self.default_config.conf.get("global", "connect_referer")))
                logging.debug("uin_request html:    " + str(info))
                if info['retcode'] != 0:
                    raise TypeError('uin to account result error')
                info = info['result']
                self.friend_list[uin_str] = info['account']

            except BaseException, error:
                logging.warning(error)

        assert isinstance(uin_str, str), "tuin is not string"
        try:
            return self.friend_list[uin_str]
        except KeyError, e:
            logging.warning(e)
            logging.debug("now uin list:    " + str(self.friend_list))
