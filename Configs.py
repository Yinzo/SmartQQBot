# -*- coding: utf-8 -*-
import ConfigParser
import os


class Configs:
<<<<<<< HEAD
=======

>>>>>>> origin/master
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()

        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists("./config/QQBot_default.conf"):
            with open("./config/QQBot_default.conf", "w") as tmp:
                tmp.close()

            self.conf.read("./config/QQBot_default.conf")
            self.conf.add_section('global')
            self.conf.add_section('pm')
            self.conf.add_section('group')
            self.conf.set('global', 'connect_referer', 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2')
            self.conf.set('global', 'smartQQ_url', 'http://w.qq.com/login.html')
            self.conf.set('global', 'QRcode_path', './v.jpg')
<<<<<<< HEAD
            self.conf.set('group', "callout", "0")
            self.conf.set('group', "repeat", "0")
=======
            self.conf.set('pm', 'QA_module_activated', '0')
            self.conf.set('group', 'tucao_module_activated', '0')
            self.conf.set('group', 'repeat_module_activated', '0')
            self.conf.set('group', 'follow_module_activated', '0')
            self.conf.set('group', 'callout_module_activated', '0')
>>>>>>> origin/master
            self.conf.write(open("./config/QQBot_default.conf", "w"))

        else:
            self.conf.read('./config/QQBot_default.conf')
<<<<<<< HEAD
            #
            # self.QRcode_path = self.conf.get("global", "QRcode_path")
            # self.smartQQ_url = self.conf.get("global", "smartQQ_url")
            # self.connect_referer = self.conf.get("global", "connect_referer")
            #
            # self.QA_activated = bool(self.conf.getint("pm", "QA_module_activated"))
            #
            # self.tucao_activated = bool(self.conf.getint("group", "tucao_module_activated"))
            # self.repeat_activated = bool(self.conf.getint("group", "repeat_module_activated"))
            # self.follow_activated = bool(self.conf.getint("group", "follow_module_activated"))
            # self.callout_activated = bool(self.conf.getint("group", "callout_module_activated"))


class GroupConfig:
    def __init__(self, group):
        self.conf = ConfigParser.ConfigParser()
        self.group = group
        self.config_file_name = str(group.gid) + ".conf"
        self.config_path = "./config/" + self.config_file_name
        self.global_config = Configs()

        self.check_config_files_exists()
        self.conf.read(self.config_path)

    # def activated_func_list(self):
    #     self.check_config_files_exists()
    #     self.conf.read(self.config_path)
    #     activated_list = []
    #     for option in self.conf.options('group'):
    #         if self.conf.getint('group', option):
    #             activated_list.append(option)
    #     return activated_list

    def check_config_files_exists(self):
        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists(self.config_path):
            self.set_default()

    def set_default(self):
        with open(self.config_path, "w") as tmp:
            tmp.close()
        self.conf.read(self.config_path)
        self.conf.add_section('group')
        for option in self.global_config.conf.options("group"):
            self.conf.set("group", option, self.global_config.conf.get("group", option))
        self.conf.write(open(self.config_path, "w"))
=======

            self.QRcode_path = self.conf.get("global", "QRcode_path")
            self.smartQQ_url = self.conf.get("global", "smartQQ_url")
            self.connect_referer = self.conf.get("global", "connect_referer")

            self.QA_activated = bool(self.conf.getint("pm", "QA_module_activated"))

            self.tucao_activated = bool(self.conf.getint("group", "tucao_module_activated"))
            self.repeat_activated = bool(self.conf.getint("group", "repeat_module_activated"))
            self.follow_activated = bool(self.conf.getint("group", "follow_module_activated"))
            self.callout_activated = bool(self.conf.getint("group", "callout_module_activated"))


class GroupConfig:

    def __init__(self, group):
        self.conf = ConfigParser.ConfigParser()
        config_file_name = str(group.gid) + ".conf"
        config_path = "./config/" + config_file_name
        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists(config_path):
            with open(config_path, "w") as tmp:
                tmp.close()

            self.conf.read(config_path)
            self.conf.add_section('group')
            self.conf.set('group', 'tucao_module_activated', '0')
            self.conf.set('group', 'repeat_module_activated', '0')
            self.conf.set('group', 'follow_module_activated', '0')
            self.conf.set('group', 'callout_module_activated', '0')
            self.conf.write(open(config_path, "w"))

        self.conf.read(config_path)
        self.tucao_activated = bool(self.conf.getint("group", "tucao_module_activated"))
        self.repeat_activated = bool(self.conf.getint("group", "repeat_module_activated"))
        self.follow_activated = bool(self.conf.getint("group", "follow_module_activated"))
        self.callout_activated = bool(self.conf.getint("group", "callout_module_activated"))
>>>>>>> origin/master
