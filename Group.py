# -*- coding: utf-8 -*-

import cPickle

from QQLogin import *
from Configs import *
from Msg import *
from HttpClient import *


class Group:

    def __init__(self, operator, ip, use_global_config=True):
        assert isinstance(operator, QQ), "Pm's operator is not a QQ"
        self.__operator = operator
        if isinstance(ip, (int, long, str)):
            # 使用uin初始化
            self.guin = ip
            self.gid = ""
        elif isinstance(ip, GroupMsg):
            self.guin = ip.from_uin
            self.gid = ip.info_seq
        self.msg_id = int(random.uniform(20000, 50000))
        self.member_list = []
        self.msg_list = []
        # TODO:消息历史保存功能
        self.follow_list = []
        self.tucao_dict = {}
        self.global_config = DefaultConfigs()
        self.private_config = GroupConfig(self)
        if use_global_config:
            self.config = self.global_config
        else:
            self.config = self.private_config
        self.process_order = [
            "repeat",
            "callout",
            "tucao",
        ]

        print str(self.gid) + "群已激活, 当前执行顺序："
        print self.process_order

        self.tucao_load()

    def handle(self, msg):
        self.config.update()
        print "msg handling."
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.process_order:
            try:
                if bool(self.config.conf.getint("group", func)):
                    print "evaling " + func
                    if eval("self." + func)(msg):
                        return func
            except ConfigParser.NoOptionError as er:
                print er, "没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数"
        print "finished."

    def reply(self, reply_content, fail_times=0):
        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
        rsp = ""
        try:
            req_url = "http://d.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r', '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(self.guin, self.__operator.client_id, self.msg_id + 1, self.__operator.psessionid, fix_content)),
                ('clientid', self.__operator.client_id),
                ('psessionid', self.__operator.psessionid)
            )
            rsp = HttpClient().Post(req_url, data, self.__operator.default_config.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply group chat error" + str(rsp_json['retcode']))
            print "Reply response: " + str(rsp_json)
            self.msg_id += 1
            return rsp_json
        except:
            if fail_times < 5:
                # loggin.error("Response Error.Wait for 2s and Retrying."+str(lastFailTimes))
                # logging.info(rsp)
                print "Response Error.Wait for 2s and Retrying." + str(fail_times)
                print rsp
                time.sleep(2)
                self.reply(reply_content, fail_times + 1)
            else:
                print "Response Error over 5 times.Exit."
                print "Content:" + str(reply_content)
                # logging.error("Response Error over 5 times.Exit.")
                # raise ValueError(rsp)
                return False

    def callout(self, msg):
        if "智障机器人" in msg.content:
            print "calling out, trying to reply...."
            self.reply("干嘛（‘·д·）")
            print str(self.gid) + "有人叫我"
            return True
        return False

    def repeat(self, msg):
        if len(self.msg_list) > 0 and self.msg_list[-1].content == msg.content:
            if str(msg.content).strip() not in ("", " ", "[图片]", "[表情]"):
                print "repeating, trying to reply..."
                self.reply(msg.content)
                print "群" + str(self.gid) + "已复读：{" + str(msg.content) + "}"
                return True
        return False

    def tucao(self, msg):
        match = re.match(r'^(?:!|！)(learn|delete) {(.+)}(?:\s*){(.+)}', msg.content)
        if match:
            command = str(match.group(1)).decode('utf8')
            key = str(match.group(2)).decode('utf8')
            value = str(match.group(3)).decode('utf8')
            if command == 'learn':
                if key in self.tucao_dict:
                    self.tucao_dict[key].append(value)
                else:
                    self.tucao_dict[key] = [value]
                self.reply("学习成功！快对我说" + str(key) + "试试吧！")
                self.tucao_save()
                return True

            elif command == 'delete':
                if key in self.tucao_dict and self.tucao_dict[key].count(value):
                    self.tucao_dict[key].remove(value)
                    self.reply("呜呜呜我再也不说" + str(value) + "了")
                    self.tucao_save()
                    return True
        else:
            for key in self.tucao_dict.keys():
                if str(key) in msg.content and self.tucao_dict[key]:
                    ran_idx = random.randint(0, len(self.tucao_dict[key]) - 1)
                    self.reply(self.tucao_dict[key][ran_idx])
                    return True
        return False


    def tucao_save(self):
        tucao_file_path = str(self.global_config.conf.get('global', 'tucao_path')) + str(self.gid) + ".tucao"
        with open(tucao_file_path, "w+") as tucao_file:
            cPickle.dump(self.tucao_dict, tucao_file)

    def tucao_load(self):
        try:
            tucao_file_path = str(self.global_config.conf.get('global', 'tucao_path'))
            tucao_file_name = tucao_file_path + str(self.gid) + ".tucao"
            os.makedirs(tucao_file_path, exist_ok=True)
            if not os.path.exists(tucao_file_name):
                with open(tucao_file_name, "w") as tmp:
                    tmp.close()
            with open(tucao_file_name, "r") as tucao_file:
                self.tucao_dict = cPickle.load(tucao_file)
        except Exception as er:
            print "读取存档出错", er
