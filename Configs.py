# -*- coding: utf-8 -*-
import ConfigParser
import os

class Configs:
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        self.config_path = "./config/QQBot_default.conf"

    def update(self):
        self.conf.read(self.config_path)

    def check_config_files_exists(self):
        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as tmp:
                tmp.close()
            self.set_default()

    def set_default(self):
        pass

class DefaultConfigs(Configs):
    def __init__(self):
        Configs.__init__(self)
        self.config_path = "./config/QQBot_default.conf"
        if not os.path.isdir("./config"):
            os.mkdir("./config")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as tmp:
                tmp.close()

            self.conf.read(self.config_path)
            self.conf.add_section('global')
            self.conf.add_section('pm')
            self.conf.add_section('group')
            self.conf.set('global', 'connect_referer', 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2')
            self.conf.set('global', 'smartQQ_url', 'http://w.qq.com/login.html')
            self.conf.set('global', 'qrcode_path', './v.jpg')

            self.conf.set('pm', "callout", "0")

            self.conf.set('group', "callout", "0")
            self.conf.set('group', "repeat", "0")

            self.conf.write(open(self.config_path, "w"))

        else:
            self.conf.read(self.config_path)

            # self.QRcode_path = self.conf.get("global", "qrcode_path")
            # self.smartQQ_url = self.conf.get("global", "smartqq_url")
            # self.connect_referer = self.conf.get("global", "connect_referer")
            #
            # self.QA_activated = bool(self.conf.getint("pm", "QA_module_activated"))
            #
            # self.tucao_activated = bool(self.conf.getint("group", "tucao_module_activated"))
            # self.repeat_activated = bool(self.conf.getint("group", "repeat_module_activated"))
            # self.follow_activated = bool(self.conf.getint("group", "follow_module_activated"))
            # self.callout_activated = bool(self.conf.getint("group", "callout_module_activated"))


class GroupConfig(Configs):
    def __init__(self, group):
        Configs.__init__(self)
        self.group = group
        self.config_file_name = str(group.gid) + ".conf"
        self.config_path = "./config/" + self.config_file_name
        self.global_config = DefaultConfigs()
        self.check_config_files_exists()
        self.conf.read(self.config_path)

    def set_default(self):
        self.conf.read(self.config_path)
        self.conf.add_section('group')
        for option in self.global_config.conf.options('group'):
            self.conf.set('group', option, self.global_config.conf.get('group', option))
        self.conf.write(open(self.config_path, 'w'))


class PmConfig(Configs):
    def __init__(self, pm):
        Configs.__init__(self)
        self.pm = pm
        self.config_file_name = str(pm.tid) + ".conf"
        self.config_path = "./config/" + self.config_file_name
        self.global_config = DefaultConfigs()
        self.check_config_files_exists()
        self.conf.read(self.config_path)

    def set_default(self):
        self.conf.read(self.config_path)
        self.conf.add_section('pm')
        for option in self.global_config.conf.options('pm'):
            self.conf.set('pm', option, self.global_config.conf.get('pm', option))
        self.conf.write(open(self.config_path, "w"))
