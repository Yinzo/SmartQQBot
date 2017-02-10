# -*- coding: utf-8 -*-
# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot
import datetime
import os
import time
import re
import json
import cgi
from random import randint
from threading import Thread

from smart_qq_bot.logger import logger
from smart_qq_bot.config import QR_CODE_PATH, SMART_QQ_REFER
from smart_qq_bot.http_client import HttpClient
from smart_qq_bot.excpetions import NeedRelogin
from smart_qq_bot.messages import (
    QMessage,
    GroupMsg,
    PrivateMsg,
    SessMsg,
    DiscussMsg,
)

QR_CODE_STATUS = {
    "qr_code_expired": 65,
    "succeed": 0,
    "unexpired": 66,
    "validating": 67,
}

MESSAGE_SENT = {
    100100,
    1202,
    0,
}


class CookieLoginFailed(UserWarning):
    pass


class QRLoginFailed(UserWarning):
    pass


def show_qr(path):
    import platform
    try:
        from six.moves.tkinter import Tk, Label
    except ImportError:
        raise SystemError('缺少Tkinter模块, 可使用sudo pip install Tkinter尝试安装')
    try:
        from PIL import ImageTk, Image
    except ImportError:
        raise SystemError('缺少PIL模块, 可使用sudo pip install PIL尝试安装')

    system = platform.system()
    if system == 'Darwin':  # 如果是Mac OS X
        img = Image.open(path)
        img.show()
    else:
        root = Tk()
        img = ImageTk.PhotoImage(
            Image.open(path)
        )
        panel = Label(root, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")
        root.mainloop()


def find_first_result(html, regxp, error, raise_exception=False):
    founds = re.findall(regxp, html)
    tip = "Can not find given pattern [%s]in response: %s" % (regxp, error)
    if not founds:
        if raise_exception:
            raise ValueError(tip)
        logger.warning(tip)
        return ''

    return founds[0]


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000


class QQBot(object):
    def __init__(self):
        self.client = HttpClient()

        # cache
        self.friend_uin_list = {}
        self._get_group_list = {}
        self.group_code_list = {}
        self._group_code_match = {}
        self.group_id_list = {}
        self.group_member_info = {}
        self.discuss_info = {}

        self._group_sig_list = {}
        self._self_info = {}

        self.client_id = 53999199
        self.ptwebqq = ''
        self.psessionid = ''
        self.appid = 0
        self.vfwebqq = ''
        self.qrcode_path = QR_CODE_PATH
        self.username = ''
        self.account = 0
        self._last_pool_success = None

    @property
    def login_out_dated(self):
        return not self._last_pool_success

    @property
    def bkn(self):
        skey = self.client.get_cookie('skey')
        hash_str = 5381
        for i in skey:
            hash_str += (hash_str << 5) + ord(i)
        hash_str = int(hash_str & 2147483647)
        return hash_str

    def _get_group_sig(self, guin, tuin, service_type=0):
        key = '%s --> %s' % (guin, tuin)
        if key not in self._group_sig_list:
            url = "http://d1.web2.qq.com/channel/get_c2cmsg_sig2?id=%s&to_uin=%s&service_type=%s&clientid=%s&psessionid=%s&t=%d" % (
                guin, tuin, service_type, self.client_id, self.psessionid, int(time.time() * 100))
            response = self.client.get(url)
            rsp_json = json.loads(response)
            if rsp_json["retcode"] != 0:
                return ""
            sig = rsp_json["result"]["value"]
            self._group_sig_list[key] = sig
        if key in self._group_sig_list:
            return self._group_sig_list[key]
        return ""

    def _login_by_cookie(self):
        logger.info("Try cookie login...")

        self.client.load_cookie()
        self.ptwebqq = self.client.get_cookie('ptwebqq')

        response = self.client.post(
            'http://d1.web2.qq.com/channel/login2',
            {
                'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(
                    self.ptwebqq,
                    self.client_id,
                    self.psessionid
                )
            },
            SMART_QQ_REFER
        )

        retry_times = 5
        while True:
            try:
                ret = json.loads(response)
                break
            except ValueError:
                retry_times -= 1
                logger.exception(
                    "Cookies login fail, response decode error:{0}".format(response)
                )
                if retry_times == 0:
                    raise CookieLoginFailed("Cookies login fail, response decode error too many times")
        if ret['retcode'] != 0:
            raise CookieLoginFailed("Login step 1 failed with response:\n %s " % ret)

        response2 = self.client.get(
            "http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid={1}&psessionid={2}&t={3}".format(
                self.ptwebqq,
                self.client_id,
                self.psessionid,
                self.client.get_timestamp()
            )
        )
        ret2 = json.loads(response2)
        if ret2['retcode'] != 0:
            raise CookieLoginFailed(
                "Login step 2 failed with response:\n %s " % ret2
            )

        self.psessionid = ret['result']['psessionid']
        self.account = ret['result']['uin']
        self.vfwebqq = ret2['result']['vfwebqq']

        logger.info("Login by cookie succeed. account: %s" % self.account)
        return True

    def _login_by_qrcode(self, no_gui):
        logger.info("RUNTIMELOG Trying to login by qrcode.")
        logger.info("RUNTIMELOG Requesting the qrcode login pages...")
        qr_validation_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?' \
                            'webqq_type=10&remember_uin=1&login2qq=1&aid={0}' \
                            '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10' \
                            '&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=' \
                            '&fp=loginerroralert&action=0-0-{1}&mibao_css={2}' \
                            '&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}' \
                            '&ptqrtoken={5}'

        init_url = "https://ui.ptlogin2.qq.com/cgi-bin/login?" \
                   "daid=164&target=self&style=16&mibao_css=m_webqq" \
                   "&appid=501004106&enable_qlogin=0&no_verifyimg=1" \
                   "&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html" \
                   "&f_url=loginerroralert&strong_login=1" \
                   "&login_state=10&t=20131024001"
        html = self.client.get(
            init_url,
        )
        appid = find_first_result(
            html,
            r'<input type="hidden" name="aid" value="(\d+)" />', 'Get AppId Error',
            True
        )
        sign = find_first_result(
            html,
            r'g_login_sig=encodeURIComponent\("(.*?)"\)', 'Get Login Sign Error',
        )
        js_ver = find_first_result(
            html,
            r'g_pt_version=encodeURIComponent\("(\d+)"\)',
            'Get g_pt_version Error',
            True,
        )
        mibao_css = find_first_result(
            html,
            r'g_mibao_css=encodeURIComponent\("(.+?)"\)',
            'Get g_mibao_css Error',
            True
        )

        start_time = date_to_millis(datetime.datetime.utcnow())

        error_times = 0
        ret_code = None
        login_result = None
        redirect_url = None

        while True:
            error_times += 1
            logger.info("Downloading QRCode file...")
            self.client.download(
                'https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(appid),
                self.qrcode_path
            )
            qrsig = self.client.get_cookie('qrsig')
            if not no_gui:
                thread = Thread(target=show_qr, args=(self.qrcode_path, ))
                thread.setDaemon(True)
                thread.start()

            while True:
                ret_code, redirect_url = self._get_qr_login_status(
                    qr_validation_url, appid, start_time, mibao_css, js_ver,
                    sign, init_url, qrsig
                )

                if ret_code in (
                        QR_CODE_STATUS['succeed'], QR_CODE_STATUS["qr_code_expired"]
                ):
                    break
                time.sleep(1)

            if ret_code == QR_CODE_STATUS['succeed'] or error_times > 10:
                break

        if os.path.exists(self.qrcode_path):
            os.remove(self.qrcode_path)

        login_failed_tips = "QRCode validation response is:\n%s" % login_result

        if ret_code is not None and (ret_code != 0):
            raise QRLoginFailed(login_failed_tips)
        elif redirect_url is None:
            raise QRLoginFailed(login_failed_tips)
        else:
            html = self.client.get(redirect_url)
            logger.debug("QR Login redirect_url response: %s" % html)
            return True

    def _hash_for_qrsig(self, qrsig):
        e = 0
        for i in qrsig:
            e += (e << 5) + ord(i)
        return 2147483647 & e;

    def _get_qr_login_status(
            self, qr_validation_url, appid, star_time,
            mibao_css, js_ver, sign, init_url, qrsig
    ):
        redirect_url = None
        login_result = self.client.get(
            qr_validation_url.format(
                appid,
                date_to_millis(datetime.datetime.utcnow()) - star_time,
                mibao_css,
                js_ver,
                sign,
                self._hash_for_qrsig(qrsig)
            ),
            init_url
        )
        ret_code = int(find_first_result(login_result, r"\d+", None))
        redirect_info = re.findall(r"(http.*?)\'", login_result)
        if redirect_info:
            logger.debug("redirect_info match is: %s" % redirect_info)
            redirect_url = redirect_info[0]
        return ret_code, redirect_url

    def login(self, no_gui=False):
        try:
            self._login_by_cookie()
        except CookieLoginFailed:
            logger.exception(CookieLoginFailed)
            while True:
                if self._login_by_qrcode(no_gui):
                    if self._login_by_cookie():
                        break
                time.sleep(4)
        user_info = self.get_self_info()
        self.get_online_friends_list()
        self.get_group_list_with_group_id()
        self.get_group_list_with_group_code()
        try:
            self.username = user_info['nick']
            logger.info(
                "User information got: user name is [%s]" % self.username
            )
            self._last_pool_success = True
        except KeyError:
            logger.exception(
                "User info access failed, check your login and response:\n%s"
                % user_info
            )
            exit(1)
        logger.info("RUNTIMELOG QQ：{0} login successfully, Username：{1}".format(self.account, self.username))

    def check_msg(self):

        # Pooling the message
        response = self.client.post(
            'http://d1.web2.qq.com/channel/poll2',
            {
                'r': json.dumps(
                    {
                        "ptwebqq": self.ptwebqq,
                        "clientid": self.client_id,
                        "psessionid": self.psessionid,
                        "key": ""
                    }
                )
            },
            SMART_QQ_REFER
        )
        logger.debug("Pooling returns response: %s" % response)
        if response == "":
            return
        try:
            ret = json.loads(response)
        except ValueError:
            logger.warning("RUNTIMELOG decode poll response error.")
            logger.debug("RESPONSE {}".format(response))
            return

        ret_code = ret['retcode']

        if ret_code in (0, 116):
            self._last_pool_success = True
            if ret_code == 0:
                if 'result' not in ret or len(ret['result']) == 0:
                    logger.info("Pooling ends, no new message received.")
                else:
                    return ret['result']
            elif ret_code == 116:
                self.ptwebqq = ret['p']
                logger.debug("ptwebqq updated in this pooling")
        else:
            self._last_pool_success = False
            if ret_code in (103, ):
                logger.warning("Pooling received retcode: " + str(ret_code))
            elif ret_code in (121,):
                logger.warning("Pooling error with retcode %s" % ret_code)
            elif ret_code == 100006:
                logger.error("Pooling request error, response is: %s" % ret)
            elif ret_code == 100012:
                raise NeedRelogin("Login is expired. Please relogin by qrcode")
            else:
                logger.warning("Pooling returns unknown retcode %s" % ret_code)
        return None

    def uin_to_account(self, tuin):
        """
        将uin转换成用户QQ号
        :param tuin:
        :return:str 用户QQ号
        """
        uin_str = str(tuin)
        try:
            logger.info("RUNTIMELOG Requesting the account by uin:    " + str(tuin))
            info = json.loads(
                self.client.get(
                    'http://s.web2.qq.com/api/get_friend_uin2?tuin={0}&type=1&vfwebqq={1}&t={2}'.format(
                        uin_str,
                        self.vfwebqq,
                        self.client.get_timestamp()
                    ),
                    SMART_QQ_REFER
                )
            )
            logger.debug("RESPONSE uin_to_account html:    " + str(info))
            if info['retcode'] != 0:
                raise TypeError('uin_to_account retcode error')
            info = info['result']['account']
            return info

        except Exception:
            logger.exception("RUNTIMELOG uin_to_account fail")
            return None

    def get_self_info(self):
        """
        获取自己的信息, 并存入self._self_info
        get_self_info2
        {"retcode":0,"result":{"birthday":{"month":1,"year":1989,"day":30},"face":555,"phone":"","occupation":"","allow":1,"college":"","uin":2609717081,"blood":0,"constel":1,"lnick":"","vfwebqq":"68b5ff5e862ac589de4fc69ee58f3a5a9709180367cba3122a7d5194cfd43781ada3ac814868b474","homepage":"","vip_info":0,"city":"青岛","country":"中国","personal":"","shengxiao":5,"nick":"要有光","email":"","province":"山东","account":2609717081,"gender":"male","mobile":""}}
        :return:dict
        """
        try_times = 0

        while len(self._self_info) is 0:
            url = "http://s.web2.qq.com/api/get_self_info2?t={}".format(time.time())
            response = self.client.get(url)
            logger.debug("get_self_info2 response:{}".format(response))
            rsp_json = json.loads(response)
            if rsp_json["retcode"] != 0:
                try_times += 1
                logger.warning("get_self_info2 fail. {}".format(try_times))
                if try_times >= 5:
                    return {}
                continue
            try:
                self._self_info = rsp_json["result"]
            except KeyError:
                logger.warning("get_self_info2 failed. Retrying.")
                continue
        return self._self_info

    def get_online_friends_list(self):
        """
        获取在线好友列表
        get_online_buddies2
        :return:list
        """
        retry_times = 10
        while retry_times:
            logger.info("RUNTIMELOG Requesting the online buddies.")
            response = self.client.get(
                'http://d1.web2.qq.com/channel/get_online_buddies2?vfwebqq={0}&clientid={1}&psessionid={2}&t={3}'.format(
                    self.vfwebqq,
                    self.client_id,
                    self.psessionid,
                    self.client.get_timestamp(),
                )
            )  # {"result":[],"retcode":0}
            logger.debug("RESPONSE get_online_buddies2 html:{}".format(response))
            try:
                online_buddies = json.loads(response)
            except ValueError:
                logger.warning("get_online_buddies2 response decode as json fail.")
                return None
            if online_buddies['retcode'] != 0:
                logger.warning('get_online_buddies2 retcode is not 0. returning.')
                return None
            online_buddies = online_buddies['result']
            return online_buddies

    def get_friend_info(self, tuin):
        """
        获取好友详情信息
        get_friend_info
        {"retcode":0,"result":{"face":0,"birthday":{"month":1,"year":1989,"day":30},"occupation":"","phone":"","allow":1,"college":"","uin":3964575484,"constel":1,"blood":3,"homepage":"http://blog.lovewinne.com","stat":20,"vip_info":0,"country":"中国","city":"","personal":"","nick":" 信","shengxiao":5,"email":"John123951@126.com","province":"山东","gender":"male","mobile":"158********"}}
        :return:dict
        """

        uin = str(tuin)
        if uin not in self.friend_uin_list:
            logger.info("RUNTIMELOG Requesting the account info by uin: {}".format(uin))
            info = json.loads(self.client.get(
                'http://s.web2.qq.com/api/get_friend_info2?tuin={0}&vfwebqq={1}&clientid={2}&psessionid={3}&t={4}'.format(
                    uin,
                    self.vfwebqq,
                    self.client_id,
                    self.psessionid,
                    self.client.get_timestamp()
                )
            ))
            logger.debug("get_friend_info2 html: {}".format(str(info)))
            if info['retcode'] != 0:
                logger.warning('get_friend_info2 retcode unknown: {}'.format(info))
                return None
            info = info['result']
            info['account'] = self.uin_to_account(uin)
            info['longnick'] = self.get_friend_longnick(uin)
            self.friend_uin_list[uin] = info

        try:
            return self.friend_uin_list[uin]
        except:
            logger.warning("RUNTIMELOG get_friend_info return fail.")
            logger.debug("RUNTIMELOG now uin list:    " + str(self.friend_uin_list[uin]))

    def get_friend_longnick(self, tuin):
        """
        获取好友的签名信息
        {"retcode":0,"result":[{"uin":3964575484,"lnick":"幸福，知道自己在哪里，知道下一个目标在哪里，心不累~"}]}
        :return:dict
        """
        url = "http://s.web2.qq.com/api/get_single_long_nick2?tuin=%s&vfwebqq=%s&t=%s" % (
            tuin, self.vfwebqq, int(time.time() * 100))
        response = self.client.get(url)
        rsp_json = json.loads(response)
        if rsp_json["retcode"] != 0:
            return {}
        return rsp_json["result"]

    def get_group_list_with_group_code(self):
        """
        获取包含群名和group_code的列表, 并存入cache, 其中code为group_code
        :type group_code: str
        :return:list
        [
            {
                u 'code': 1131597161, # 这是真实group_code
                u 'flag': 184550417,
                u 'gid': 1802239929,  # 这是msg.group_code, 即假group_code
                u 'name': u '测试'
            },
            {
                u 'code': 1131597161,
                u 'flag': 184550417,
                u 'gid': 1802239929,
                u 'name': u '测试'
            }
        ]
        """

        def _hash_digest(uin, ptwebqq):
            """
            计算hash，貌似TX的这个算法会经常变化，暂时不使用
            get_group_list_with_group_code 会依赖此数据
            提取自http://pub.idqqimg.com/smartqq/js/mq.js
            :param uin:
            :param ptwebqq:
            :return:
            """
            N = [0, 0, 0, 0]
            # print(N[0])
            for t in range(len(ptwebqq)):
                N[t % 4] ^= ord(ptwebqq[t])
            U = ["EC", "OK"]
            V = [0, 0, 0, 0]
            V[0] = int(uin) >> 24 & 255 ^ ord(U[0][0])
            V[1] = int(uin) >> 16 & 255 ^ ord(U[0][1])
            V[2] = int(uin) >> 8 & 255 ^ ord(U[1][0])
            V[3] = int(uin) & 255 ^ ord(U[1][1])
            U = [0, 0, 0, 0, 0, 0, 0, 0]
            for T in range(8):
                if T % 2 == 0:
                    U[T] = N[T >> 1]
                else:
                    U[T] = V[T >> 1]
            N = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
            V = ""
            for T in range(len(U)):
                V += N[U[T] >> 4 & 15]
                V += N[U[T] & 15]
            return V


        logger.info("RUNTIMELOG Requesting the group list.")
        response = self.client.post(
            'http://s.web2.qq.com/api/get_group_name_list_mask2',
            {
                'r': json.dumps(
                    {
                        "vfwebqq": self.vfwebqq,
                        "hash": _hash_digest(self._self_info['uin'], self.ptwebqq),
                    }
                )
            },
        )
        try:
            response = json.loads(response)
        except ValueError:
            logger.warning("RUNTIMELOG The response of group list request can't be load as json")
            return
        logger.debug("RESPONSE get_group_name_list_mask2 html:    " + str(response))
        if response['retcode'] != 0:
            raise TypeError('get_group_list_with_group_code result error')
        for group in response['result']['gnamelist']:
            self.group_code_list[str(group['gid'])] = group
            self.group_code_list[str(group['code'])] = group

        return response['result']['gnamelist']

    def get_group_list_with_group_id(self):
        """
        获取包含群名和群号的列表, 并存入cache, 其中gc为群号
        :type group_id: str
        :return:list

        return list sample
        [
            {
                "gc": 114302207,
                "gn": "测试群1",
                "owner": 484216451
            },
            {
                "gc": 125299202,
                "gn": "测试群2",
                "owner": 242917661
            }
        ]
        """
        if self._get_group_list:
            response = self._get_group_list
        else:
            url = "http://qun.qq.com/cgi-bin/qun_mgr/get_group_list"
            data = {'bkn': self.bkn}
            response = self.client.post(url, data=data, refer='http://qun.qq.com/member.html')
            self._get_group_list = response
            logger.debug("get_group_list response: {}".format(response))
        rsp_json = json.loads(response)
        if rsp_json['ec'] == 0:
            group_id_list = list()
            group_id_list.extend(rsp_json.get('join') or [])
            group_id_list.extend(rsp_json.get('manage') or [])
            group_id_list.extend(rsp_json.get('create') or [])
            if group_id_list:
                for group in group_id_list:
                    self.group_id_list[str(group['gc'])] = group
                return group_id_list
            else:
                logger.warning("seems this account didn't join any group: {}".format(response))
                return []
        else:
            logger.warning("get_group_list code unknown: {}".format(response))
            return None

    def get_true_group_code(self, fake_group_code):
        """
        通过假group_code获取真group_code
        :type fake_group_code: str
        :return str
        """
        if self._group_code_match.get(str(fake_group_code)):
            return self._group_code_match.get(str(fake_group_code))
        else:
            fake_group_code = str(fake_group_code)
            logger.debug("正在查询group_code:{}对应的真实group_code".format(fake_group_code))
            if fake_group_code not in self.group_code_list:
                logger.info("尝试更新群列表信息")
                self.get_group_list_with_group_code()  # 先尝试更新群列表
                if fake_group_code not in self.group_code_list:
                    logger.warning("没有所查询的group_code, 请检查group_code是否错误")
                    return 0
            true_group_code = str(self.group_code_list[fake_group_code]['code'])
            self._group_code_match[str(fake_group_code)] = true_group_code
            return true_group_code

    def get_group_info(self, group_code=None, group_id=None):
        """
        通过group_code或者group_id(群号)获取对应群信息
        :type group_code: str
        :type group_id: str
        :return dict
        {
            'name':         "群名",
            'id':            12345678,
            'group_code':    87654321
        }
        """
        if group_code or group_id:
            if group_code:
                assert isinstance(group_code, str), "group_code类型错误, 应该为str"
                t_group_code = self.get_true_group_code(group_code)
                if t_group_code not in self.group_code_list and group_code not in self.group_code_list:
                    self.get_group_list_with_group_code()
                group_code_info = self.group_code_list.get(t_group_code) or self.group_code_list.get(group_code)

                group_id_list = self.get_group_list_with_group_id()
                result = {
                    'name':         group_code_info['name'] or "",
                    'id':           0,
                    'group_code':   group_code_info['code'] or 0
                }
                name = cgi.escape(group_code_info['name']).replace(' ', '&nbsp;')
                group_id_list = [x for x in group_id_list if x['gn'] == name]
                if len(group_id_list) == 1:
                    result['id'] = group_id_list[0].get('gc')
                    return result
                elif len(group_id_list) > 1:
                    raise KeyError('QQ{qq}的群列表中含有{count}个同名群:"{group_name}"'.format(
                        qq=self.account,
                        count=len(group_id_list),
                        group_name=group_code_info['name']
                    ))
            elif group_id:
                assert isinstance(group_id, str), "group_id类型错误, 应该为str"
                if group_id not in self.group_id_list:
                    self.get_group_list_with_group_id()
                group_id_info = self.group_id_list.get(group_id)
                group_code_list = self.get_group_list_with_group_code()
                result = {
                    'name': group_id_info['gn'] or "",
                    'id': group_id_info['gc'] or 0,
                    'group_code': 0
                }
                group_code_list = [
                    x for x in group_code_list
                    if x['name'] == group_id_info['gn']
                ]
                if len(group_code_list) == 1:
                    result['group_code'] = group_code_list[0].get('code')
                    return result
                else:
                    raise KeyError('QQ{qq}的群列表中含有{count}个同名群:"{group_name}"'.format(
                        qq=self.account,
                        count=len(group_code_list),
                        group_name=group_id_info['gn']
                    ))
        else:
            raise KeyError("请输入group_code或group_id之一")

    def get_group_member_info_list(self, group_code):
        """
        获取指定群的成员信息
        :group_code: int, can be "ture" of "fake" group_code
        {"retcode":0,"result":{"stats":[],"minfo":[{"nick":" 信","province":"山东","gender":"male","uin":3964575484,"country":"中国","city":""},{"nick":"崔震","province":"","gender":"unknown","uin":2081397472,"country":"","city":""},{"nick":"云端的猫","province":"山东","gender":"male","uin":3123065696,"country":"中国","city":"青岛"},{"nick":"要有光","province":"山东","gender":"male","uin":2609717081,"country":"中国","city":"青岛"},{"nick":"小莎机器人","province":"广东","gender":"female","uin":495456232,"country":"中国","city":"深圳"}],"ginfo":{"face":0,"memo":"http://hujj009.ys168.com\r\n0086+区(没0)+电话\r\n0086+手机\r\nhttp://john123951.xinwen365.net/qq/index.htm","class":395,"fingermemo":"","code":3943922314,"createtime":1079268574,"flag":16778241,"level":0,"name":"ぁQQぁ","gid":3931577475,"owner":3964575484,"members":[{"muin":3964575484,"mflag":192},{"muin":2081397472,"mflag":65},{"muin":3123065696,"mflag":128},{"muin":2609717081,"mflag":0},{"muin":495456232,"mflag":0}],"option":2},"cards":[{"muin":3964575484,"card":"●s.Εx2(22222)□"},{"muin":495456232,"card":"小莎机器人"}],"vipinfo":[{"vip_level":0,"u":3964575484,"is_vip":0},{"vip_level":0,"u":2081397472,"is_vip":0},{"vip_level":0,"u":3123065696,"is_vip":0},{"vip_level":0,"u":2609717081,"is_vip":0},{"vip_level":0,"u":495456232,"is_vip":0}]}}
        :return:dict
        """
        if group_code == 0:
            return
        try:
            url = "http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s&vfwebqq=%s&t=%s" % (
                group_code, self.vfwebqq, int(time.time() * 100))
            response = self.client.get(url)
            rsp_json = json.loads(response)
            logger.debug("get_group_member_info_list info response: {}".format(rsp_json))
            retcode = rsp_json["retcode"]
            if retcode == 0:
                result = rsp_json["result"]
            elif retcode == 6:
                logger.debug("get_group_member_info_list retcode is 6, trying to get true code.")
                result = self.get_group_member_info_list(self.get_true_group_code(group_code))
            else:
                logger.warning("group_code error.")
                return
            self.group_member_info[str(group_code)] = result    # 缓存群成员信息, 此处会把真假group_code都加入cache
            return result
        except Exception as ex:
            logger.warning("RUNTIMELOG get_group_member_info_list. Error: " + str(ex))
            return

    def get_group_member_info(self, group_code, uin):
        """
        获取群中某一指定成员的信息
        :type group_code:   int, can be "ture" of "fake" group_code
        :type uin:  int
        :return:    dict
        {
            u 'province': u '',
            u 'city': u '',
            u 'country': u '',
            u 'uin': 2927049915,
            u 'nick': u 'Auro',
            u 'gender': u 'male',
            u 'card': u 'Yinzo'
        }
        """
        group_code = str(group_code)
        if group_code not in self.group_member_info:
            logger.info("group_code not in cache, try to request info")
            result = self.get_group_member_info_list(group_code)
            if result is False:
                logger.warning("没有所查询的group_code信息")
                return

        result_dict = {}
        for member in self.group_member_info[group_code].get('minfo') or []:
            if member.get('uin') == uin:
                result_dict = member
                break

        for card_dict in self.group_member_info[group_code].get('cards') or []:
            if card_dict.get('muin') == uin:
                result_dict['card'] = card_dict.get('card')
                break

        return result_dict

    def search_group_members(self, group_id):
        """
        获取群成员详细信息的的列表, uin为真实QQ号, 并存入cache
        :type group_id: str
        :return:list

        return list sample
        [
            {
              "card": "群名片",
              "flag": 0,
              "g": 255,
              "join_time": 1385383309,
              "last_speak_time": 1471325570,
              "lv": {
                "level": 6,
                "point": 5490
              },
              "nick": "昵称",
              "qage": 0,
              "role": 0,
              "tags": "-1",
              "uin": 493658555
            }
        ]
        """
        url = "http://qun.qq.com/cgi-bin/qun_mgr/search_group_members"
        data = {
            'bkn':  self.bkn,
            'gc':   str(group_id),
            'st':   0,
            'end':  2000,
            'sort': 0,
        }
        response = self.client.post(url, data=data, refer='http://qun.qq.com/member.html')
        logger.debug("search_group_members response: {}".format(response))
        rsp_json = json.loads(response)
        if rsp_json['ec'] == 0:
            return rsp_json.get('mems')
        else:
            logger.warning("search_group_members code unknown: {}".format(response))
            return None

    def get_discuss_info(self, did):
        """
        获取指定讨论组的成员信息
        :did: str
        {u'result': {u'info': {u'did': 2966596468, u'discu_name': u'', u'mem_list': [{u'ruin': 466331599, u'mem_uin': 466331599}, {u'ruin': 493658515, u'mem_uin': 556813270}, {u'ruin': 824566900, u'mem_uin': 2606746705}]}, u'mem_status': [], u'mem_info': [{u'nick': u'\\u54a6', u'uin': 466331599}, {u'nick': u'Auro', u'uin': 556813270}, {u'nick': u'-', u'uin': 2606746705}]}, u'retcode': 0}
        :rtype: dict
        """
        if did == 0:
            return
        try:
            did = str(did)
            url = "http://d1.web2.qq.com/channel/get_discu_info?did={did}&psessionid={psessionid}&vfwebqq={vfwebqq}&clientid={clientid}&t={t}".format(
                did=did, psessionid=self.psessionid, vfwebqq=self.vfwebqq, clientid=self.client_id,
                t=int(time.time() * 100)
            )
            response = self.client.get(url)
            rsp_json = json.loads(response)
            logger.debug("get_discuss_info response: {}".format(rsp_json))
            retcode = rsp_json["retcode"]
            if retcode == 0:
                result = rsp_json["result"]
            else:
                logger.warning("get_discuss_info error.")
                return
            self.discuss_info[str(did)] = result  # 缓存群成员信息, 此处会把真假group_code都加入cache
            return result
        except Exception as ex:
            logger.warning("get_discuss_info error: " + str(ex))
            return

    def get_discuss_member_info(self, did, uin):
        """
        获取讨论组中某一指定成员的信息
        :type did:   str
        :type uin:  int
        :return:    dict
        {
            "nick": "Yinzo",
            "uin": 3642699982
        }
        """
        did = str(did)
        if did not in set(self.discuss_info.keys()):
            logger.info("did(discuss_id) not in cache, try to request info")
            result = self.get_discuss_info(did)
            if result is False:
                logger.warning("没有所查询的discuss_id信息")
                return

        for member in self.discuss_info[did]['mem_info']:
            if member['uin'] == int(uin):
                return member

    # 发送群消息
    def send_group_msg(self, reply_content, group_code, msg_id, fail_times=0):
        chunk_length = 500
        for i in range(0, len(reply_content), chunk_length):
            reply_content_partial = reply_content[0+i:chunk_length+i]
            ret = self.send_group_msg_partial(reply_content_partial, group_code, msg_id, fail_times)
        return ret;

    # 发送部分群消息
    def send_group_msg_partial(self, reply_content, group_code, msg_id, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t"))
        rsp = ""
        try:
            logger.info("Starting send group message: %s" % reply_content)
            req_url = "http://d1.web2.qq.com/channel/send_qun_msg2"
            data = {
                'r':
                 '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":{1},"msg_id":{2},"psessionid":"{3}"}}'.format(
                         group_code, self.client_id, msg_id, self.psessionid, fix_content),
                'clientid': self.client_id,
                'psessionid': self.psessionid
            }
            rsp = self.client.post(req_url, data, SMART_QQ_REFER)
            rsp_json = json.loads(rsp)
            if 'retcode' in rsp_json and rsp_json['retcode'] not in MESSAGE_SENT:
                raise ValueError("RUNTIMELOG reply group chat error" + str(rsp_json['retcode']))
            logger.info("RUNTIMELOG send_qun_msg: Reply '{}' successfully.".format(reply_content))
            logger.debug("RESPONSE send_qun_msg: Reply response: " + str(rsp))
            return rsp_json
        except:
            logger.warning("RUNTIMELOG send_qun_msg fail")
            if fail_times < 5:
                logger.warning("RUNTIMELOG send_qun_msg: Response Error.Wait for 2s and Retrying." + str(fail_times))
                logger.debug("RESPONSE send_qun_msg rsp:" + str(rsp))
                time.sleep(2)
                self.send_group_msg(reply_content, group_code, msg_id, fail_times + 1)
            else:
                logger.warning("RUNTIMELOG send_qun_msg: Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False


    # 发送私密消息
    def send_friend_msg(self, reply_content, uin, msg_id, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t"))
        rsp = ""
        try:
            req_url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
            data = {
                'r':
                 '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":{1}, "msg_id":{2}, "psessionid":"{3}"}}'.format(
                         uin, self.client_id, msg_id, self.psessionid, fix_content),
                'clientid': self.client_id,
                'psessionid': self.psessionid
            }
            rsp = self.client.post(req_url, data, SMART_QQ_REFER)
            rsp_json = json.loads(rsp)
            if 'errCode' in rsp_json and rsp_json['errCode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
            logger.info("RUNTIMELOG Reply successfully.")
            logger.debug("RESPONSE Reply response: " + str(rsp))
            return rsp_json
        except:
            if fail_times < 5:
                logger.warning("RUNTIMELOG Response Error.Wait for 2s and Retrying." + str(fail_times))
                logger.debug("RESPONSE " + str(rsp))
                time.sleep(2)
                self.send_friend_msg(reply_content, uin, msg_id, fail_times + 1)
            else:
                logger.warning("RUNTIMELOG Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False

    # 发送讨论组消息
    def send_discuss_msg(self, reply_content, did, msg_id, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t"))
        rsp = ""
        try:
            logger.info("Starting send discuss group message: %s" % reply_content)
            req_url = "http://d1.web2.qq.com/channel/send_discu_msg2"
            data = {
                'r':
                 '{{"did":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":{1},"msg_id":{2},"psessionid":"{3}"}}'.format(
                         did, self.client_id, msg_id, self.psessionid, fix_content),
                'clientid': self.client_id,
                'psessionid': self.psessionid
            }
            rsp = self.client.post(req_url, data, SMART_QQ_REFER)
            rsp_json = json.loads(rsp)
            if 'retcode' in rsp_json and rsp_json['retcode'] not in MESSAGE_SENT:
                raise ValueError("RUNTIMELOG reply discuss group error" + str(rsp_json['retcode']))
            logger.info("send_discuss_msg: Reply '{}' successfully.".format(reply_content))
            logger.debug("send_discuss_msg: Reply response: " + str(rsp))
            return rsp_json
        except:
            logger.warning("send_discuss_msg fail")
            if fail_times < 5:
                logger.warning("send_discuss_msg: Response Error.Wait for 2s and Retrying." + str(fail_times))
                logger.debug("send_discuss_msg response:" + str(rsp))
                time.sleep(2)
                self.send_group_msg(reply_content, did, msg_id, fail_times + 1)
            else:
                logger.warning("RUNTIMELOG send_qun_msg: Response Error over 5 times.Exit.reply content:" + str(reply_content))
                return False


    def reply_msg(self, msg, reply_content=None, return_function=False):
        """
        :type msg: QMessage类, 例如 GroupMsg, PrivateMsg, SessMsg
        :type reply_content: string, 回复的内容.
        :return: 服务器的响应内容. 如果 return_function 为 True, 则返回的是一个仅有 reply_content 参数的便捷回复函数.
        """
        msg_id = randint(1, 100000)
        import functools
        assert isinstance(msg, QMessage)
        if isinstance(msg, GroupMsg):
            if return_function:
                return functools.partial(self.send_group_msg, group_code=msg.group_code, msg_id=msg_id)
            return self.send_group_msg(reply_content=reply_content, group_code=msg.group_code, msg_id=msg_id)
        elif isinstance(msg, PrivateMsg):
            if return_function:
                return functools.partial(self.send_friend_msg, uin=msg.from_uin, msg_id=msg_id)
            return self.send_friend_msg(reply_content=reply_content, uin=msg.from_uin, msg_id=msg_id)
        elif isinstance(msg, SessMsg):
            # 官方已废弃临时消息接口, 等官方重启后再完善此函数
            pass
        elif isinstance(msg, DiscussMsg):
            if return_function:
                return functools.partial(self.send_discuss_msg, did=msg.did, msg_id=msg_id)
            return self.send_discuss_msg(reply_content=reply_content, did=msg.did, msg_id=msg_id)
