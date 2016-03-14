# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

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
            self.conf.add_section('sess')
            self.conf.set('global', 'connect_referer', 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
            self.conf.set('global', 'smartQQ_url', 'http://w.qq.com/login.html')
            self.conf.set('global', 'qrcode_path', './v.jpg')
            self.conf.set('global', 'tucao_path', './data/tucao_save/')

            self.conf.set('pm', 'use_private_config', '0')
            self.conf.set('pm', "callout", "0")
            self.conf.set('pm', "repeat", "0")
            self.conf.set('pm', 'command_0arg', '0')
            self.conf.set('pm', 'command_1arg', '0')

            self.conf.set('group', 'use_private_config', '0')
            self.conf.set('group', "callout", "0")
            self.conf.set('group', "repeat", "0")
            self.conf.set('group', "tucao", "0")
            self.conf.set('group', "follow", "0")
            self.conf.set('group', 'command_0arg', '0')
            self.conf.set('group', 'command_1arg', '0')

            self.conf.set('sess', 'use_private_config', '0')
            self.conf.set('sess', 'callout', '0')

            self.conf.write(open(self.config_path, "w"))

        else:
            self.conf.read(self.config_path)


class GroupConfig(Configs):
    def __init__(self, group):
        Configs.__init__(self)
        self.group = group
        self.config_file_name = str(group.gid) + ".conf"
        self.config_path = "./config/group/" + self.config_file_name
        self.global_config = DefaultConfigs()
        self.check_config_files_exists()
        self.conf.read(self.config_path)

    def check_config_files_exists(self):
        if not os.path.isdir("./config/group/"):
            os.mkdir("./config/group/")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as tmp:
                tmp.close()
            self.set_default()

    def set_default(self, all_off=False):
        self.conf.read(self.config_path)
        self.conf.add_section('group')
        if all_off:
            for option in self.global_config.conf.options('group'):
                self.conf.set('group', option, '0')
        else:
            for option in self.global_config.conf.options('group'):
                self.conf.set('group', option, self.global_config.conf.get('group', option))
        self.conf.write(open(self.config_path, 'w'))


class PmConfig(Configs):
    def __init__(self, pm):
        Configs.__init__(self)
        self.pm = pm
        self.config_file_name = str(pm.tid) + ".conf"
        self.config_path = "./config/pm/" + self.config_file_name
        self.global_config = DefaultConfigs()
        self.check_config_files_exists()
        self.conf.read(self.config_path)

    def check_config_files_exists(self):
        if not os.path.isdir("./config/pm/"):
            os.mkdir("./config/pm/")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as tmp:
                tmp.close()
            self.set_default()

    def set_default(self, all_off=False):
        self.conf.read(self.config_path)
        self.conf.add_section('pm')
        if all_off:
            for option in self.global_config.conf.options('pm'):
                self.conf.set('pm', option, '0')
        else:
            for option in self.global_config.conf.options('pm'):
                self.conf.set('pm', option, self.global_config.conf.get('pm', option))
        self.conf.write(open(self.config_path, "w"))


class SessConfig(Configs):
    def __init__(self, sess):
        Configs.__init__(self)
        self.sess = sess
        self.config_file_name = str(sess.tid) + ".conf"
        self.config_path = "./config/sess/" + self.config_file_name
        self.global_config = DefaultConfigs()
        self.check_config_files_exists()
        self.conf.read(self.config_path)

    def check_config_files_exists(self):
        if not os.path.isdir("./config/sess/"):
            os.mkdir("./config/sess/")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as tmp:
                tmp.close()
            self.set_default()

    def set_default(self, all_off=False):
        self.conf.read(self.config_path)
        self.conf.add_section('sess')
        if all_off:
            for option in self.global_config.conf.options('sess'):
                self.conf.set('sess', option, '0')
        else:
            for option in self.global_config.conf.options('sess'):
                self.conf.set('sess', option, self.global_config.conf.get('sess', option))
        self.conf.write(open(self.config_path, "w"))
