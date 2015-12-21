# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import cPickle
from collections import namedtuple
from QQLogin import *
from Configs import *
from Msg import *
from plugin import shuishiwodi, shuishiwodiStartStatus
from plugin.weather import Weather
from plugin.Turing import Turing

logging.basicConfig(
    filename='smartqq.log',
    level=logging.DEBUG,
    format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


# logging.basicConfig(level=logging.DEBUG)


class Group:
    def __init__(self, operator, ip):
        assert isinstance(operator, QQ), "Pm's operator is not a QQ"
        self.__operator = operator
        if isinstance(ip, (int, long, str)):
            # 使用uin初始化
            self.guin = ip
            self.gid = ""
        elif isinstance(ip, GroupMsg):
            self.guin = ip.from_uin
            self.gid = ip.group_code
        self.msg_id = int(random.uniform(20000, 50000))
        self.group_code = 0
        self.member_list = []
        self.msg_list = []
        self.follow_list = []
        self.tucao_dict = {}
        self.global_config = DefaultConfigs()
        self.private_config = GroupConfig(self)
        self.update_config()
        self.process_order = [
            "game",
            "weather",
            'ask',
            "follow",
            "repeat",
            "callout",
            "command_0arg",
            "command_1arg",
            "tucao",
        ]
        self.__game_handler = None
        logging.info(str(self.gid) + "群已激活, 当前执行顺序： " + str(self.process_order))
        self.tucao_load()

    def update_config(self):
        self.private_config.update()
        use_private_config = bool(self.private_config.conf.getint("group", "use_private_config"))
        if use_private_config:
            self.config = self.private_config
        else:
            self.config = self.global_config
        self.config.update()

    def handle(self, msg):
        self.update_config()
        if self.group_code <= 0:
            self.group_code = msg.group_code
        logging.info("msg handling.")
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.process_order:
            try:
                if bool(self.config.conf.getint("group", func)):
                    logging.info("evaling " + func)
                    if eval("self." + func)(msg):
                        logging.info("msg handle finished.")
                        self.msg_list.append(msg)
                        return func
            except ConfigParser.NoOptionError as er:
                logging.warning(str(er) + "没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数")
        self.msg_list.append(msg)

    def get_member_list(self):
        if not self.member_list:
            result = self.__operator.get_group_info_ext2(self.group_code)
            if not result or not result["minfo"]:
                return self.member_list
            MemberInfo = namedtuple('MemberInfo', 'nick province gender uin country city')
            member_lst = map(lambda x: MemberInfo(**x), result["minfo"])
            d = {}
            if result["cards"]:
                for item in result["cards"]:
                    d[item["muin"]] = item["card"]
            if d:
                for member in member_lst:
                    key = str(member.uin)
                    if key in d:
                        member.nick = d[key]
            self.member_list = member_lst
        return self.member_list

    # 发送群消息
    def reply(self, reply_content):
        self.msg_id += 1
        return self.__operator.send_qun_msg(self.guin, reply_content, self.msg_id)

    # 发送临时消息给群成员
    def reply_sess(self, tuin, reply_content, service_type=0):
        self.msg_id += 1
        self.__operator.send_sess_msg2_fromGroup(self.guin, tuin, reply_content, self.msg_id, service_type)

    def command_0arg(self, msg):
        # webqq接受的消息会以空格结尾
        match = re.match(r'^(?:!|！)([^\s\{\}]+)\s*$', msg.content)
        if match:
            command = str(match.group(1))
            logging.info("command format detected, command: " + command)

            if command == "吐槽列表":
                self.show_tucao_list()
                return True

        return False

    def command_1arg(self, msg):
        match = re.match(r'^(?:!|！)([^\s\{\}]+)(?:\s?)\{([^\s\{\}]+)\}\s*$', msg.content)
        if match:
            command = str(match.group(1))
            arg1 = str(match.group(2))
            logging.info("command format detected, command:{0}, arg1:{1}".format(command, arg1))
            if command == "删除关键字" and unicode(arg1) in self.tucao_dict:
                self.tucao_dict.pop(unicode(arg1))
                self.reply("已删除关键字:{0}".format(arg1))
                self.tucao_save()
                return True

        return False

    def show_tucao_list(self):
        result = ""
        for key in self.tucao_dict:
            result += "关键字：{0}      回复：{1}\n".format(key, " / ".join(self.tucao_dict[key]))
        logging.info("Replying the list of tucao")
        self.reply(result)

    def callout(self, msg):
        if "智障机器人" in msg.content:
            logging.info(str(self.gid) + " calling me out, trying to reply....")
            self.reply("干嘛（‘·д·）")
            return True
        return False

    def repeat(self, msg):
        if len(self.msg_list) > 0 and self.msg_list[-1].content == msg.content:
            if str(msg.content).strip() not in ("", " ", "[图片]", "[表情]"):
                logging.info(str(self.gid) + " repeating, trying to reply " + str(msg.content))
                self.reply(msg.content)
                return True
        return False

    def tucao(self, msg):
        match = re.match(r'^(?:!|！)(learn|delete)(?:\s?){(.+)}(?:\s?){(.+)}', msg.content)
        if match:
            logging.info("tucao command detected.")
            command = str(match.group(1)).decode('utf8')
            key = str(match.group(2)).decode('utf8')
            value = str(match.group(3)).decode('utf8')
            if command == 'learn':
                if key in self.tucao_dict and value not in self.tucao_dict[key]:
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
                    logging.info("tucao pattern detected, replying...")
                    self.reply(random.choice(self.tucao_dict[key]))
                    return True
        return False

    def tucao_save(self):
        try:
            tucao_file_path = str(self.global_config.conf.get('global', 'tucao_path')) + str(self.gid) + ".tucao"
            with open(tucao_file_path, "w+") as tucao_file:
                cPickle.dump(self.tucao_dict, tucao_file)
            logging.info("tucao saved. Now tucao list:  {0}".format(str(self.tucao_dict)))
        except Exception:
            logging.error("Fail to save tucao.")
            raise IOError("Fail to save tucao.")

    def tucao_load(self):
        # try:
        tucao_file_path = str(self.global_config.conf.get('global', 'tucao_path'))
        tucao_file_name = tucao_file_path + str(self.gid) + ".tucao"
        if not os.path.isdir(tucao_file_path):
            os.makedirs(tucao_file_path)
        if not os.path.exists(tucao_file_name):
            with open(tucao_file_name, "w") as tmp:
                tmp.close()
        with open(tucao_file_name, "r") as tucao_file:
            try:
                self.tucao_dict = cPickle.load(tucao_file)
                logging.info("tucao loaded. Now tucao list:  {0}".format(str(self.tucao_dict)))
            except EOFError:
                logging.info("tucao file is empty.")
                # except Exception as er:
                #     logging.error("Fail to load tucao:  ", er)
                #     raise IOError("Fail to load tucao:  ", er)

    def follow(self, msg):
        match = re.match(r'^(?:!|！)(follow|unfollow) (\d+|me)', msg.content)
        if match:
            logging.info("following...")
            command = str(match.group(1))
            target = str(match.group(2))
            if target == 'me':
                target = str(self.__operator.uin_to_account(msg.send_uin))

            if command == 'follow' and target not in self.follow_list:
                self.follow_list.append(target)
                self.reply("我开始关注" + target + "啦")
                return True
            elif command == 'unfollow' and target in self.follow_list:
                self.follow_list.remove(target)
                self.reply("我不关注" + target + "了")
                return True
        else:
            if str(self.__operator.uin_to_account(msg.send_uin)) in self.follow_list:
                self.reply(msg.content)
                return True
        return False

    def weather(self, msg):
        match = re.match(ur'^(weather|天气) (\w+|[\u4e00-\u9fa5]+)', msg.content)
        if match:
            logging.info("查询天气...")
            print msg.content
            command = match.group(1)
            city = match.group(2)
            logging.info(msg.content)
            print city
            if command == 'weather' or command == u'天气':
                query = Weather()
                info = query.getWeatherOfCity(city)
                logging.info(str(info))
                self.reply(str(info))
                return True
        return False

    def ask(self, msg):
        match = re.match(ur'^(ask|问) (\w+|[\u4e00-\u9fa5]+)', msg.content)
        if match:
            # logging.info("问答测试...")
            print msg.content
            command = match.group(1)
            info = match.group(2)
            # logging.info("info:")
            logging.info(msg.content)
            # print info
            if command == 'ask' or command == u'问':
                # self.reply("我开始查询" + city + "的天气啦")
                query = Turing()
                info = query.getReply(info)
                logging.info(str(info))
                self.reply(str(info))
                return True
        return False

    def game(self, msg):
        match = re.match(ur'^(?:!|！)(game)\s*(\w+|[\u4e00-\u9fa5]+)?', msg.content)
        if match:
            command = str(match.group(1))
            args1 = match.group(2)
            if not args1:
                self.reply('玩游戏：!game 开始谁是卧底5人局\n结束游戏：!game end')
                return True
            if args1 == 'end':
                if self.__game_handler and self.__game_handler.statusHandle:
                    self.__game_handler.statusHandle = None
                self.__game_handler = None
                self.reply('游戏结束')
                return True
            if args1 and u'谁是卧底' in args1:
                self.__game_handler = shuishiwodi(shuishiwodiStartStatus(), self)
                self.__game_handler.run(msg)
                return True
            return True
        # 没有处理程序时退出
        if not self.__game_handler:
            return False
        # 谁是卧底的处理程序
        if isinstance(self.__game_handler, shuishiwodi):
            if self.__game_handler.status not in ['StartStatus', 'EndStatus']:
                self.__game_handler.run(msg)
                return True  # 游戏期间屏蔽其他处理过程
        return False
