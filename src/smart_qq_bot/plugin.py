# coding: utf-8
import json
import os
import shutil

from smart_qq_bot.logger import logger
from smart_qq_bot.config import DEFAULT_PLUGIN_CONFIG
from smart_qq_bot.excpetions import (
    ConfigFileDoesNotExist,
    ConfigKeyError,
)

__all__ = ("PluginManager", )

PLUGIN_PACKAGES = "plugin_packages"
PLUGIN_ON = "plugin_on"


class PluginManager(object):

    def __init__(self, config_file=None, load_now=True):
        self.config_file = config_file
        self._plugin_prefix = "smart_qq_plugins"
        self.config = {
            PLUGIN_PACKAGES: [],
            PLUGIN_ON: [],
        }
        self._load_config(config_file)
        if load_now:
            self.load_plugin()

    def load_config(self, config_file):
        """
        You can load plugin config any time, then load plugin.
        :typ config_file: str or unicode
        """
        self.config_file = config_file
        self._load_config(config_file)

    def _load_config(self, config_file):
        config = None
        if config_file is not None:
            # 指定了特定配置文件
            if os.path.isfile(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
            else:
                raise ConfigFileDoesNotExist(
                    "Config file {} does not exist.".format(config_file)
                )
        elif os.path.isfile(DEFAULT_PLUGIN_CONFIG):
            # 存在配置文件
            with open(DEFAULT_PLUGIN_CONFIG, "r") as f:
                config = json.load(f)

        elif os.path.isfile(DEFAULT_PLUGIN_CONFIG + ".example"):
            # 不存在配置文件但有example文件
            shutil.copy(DEFAULT_PLUGIN_CONFIG + ".example", DEFAULT_PLUGIN_CONFIG)
            logger.warning("No plugin config file found. Auto copied.")
            with open(DEFAULT_PLUGIN_CONFIG, "r") as f:
                config = json.load(f)
        else:
            # 缺少配置文件以及example文件
            exception_str = "Config file does not exist, please check the config path."
            logger.exception(exception_str)
            raise ConfigFileDoesNotExist(exception_str)

        if config is not None:
            for key in ("plugin_package", PLUGIN_ON):
                if not isinstance(config.get("plugin_package", []), list):
                    raise ConfigKeyError(
                        "Config key [%s] has wrong type [%s]"
                        % (key, type(config[PLUGIN_PACKAGES]))
                    )
            self.config[PLUGIN_PACKAGES] = config[PLUGIN_PACKAGES]
            self.config[PLUGIN_ON] = config[PLUGIN_ON]

    def load_plugin(self):
        self._load_default()
        self._load_package_plugin()

    def _gen_plugin_name(self, name):
        return "%s.%s" % (self._plugin_prefix, name)

    def _load_package_plugin(self):
        for package_name in self.config[PLUGIN_PACKAGES]:
            try:
                __import__(package_name)
                logger.info("Package plugin [%s] loaded." % package_name)
            except ImportError:
                logger.error(
                    "Package plugin import error: can not import [%s]"
                    % package_name
                )

    def _load_default(self):
        for plugin_name in self.config[PLUGIN_ON]:
            try:
                __import__(self._gen_plugin_name(plugin_name))
                logger.info("Plugin [%s] loaded." % plugin_name)
            except ImportError:
                logger.error(
                    "Internal plugin import error: can not import [%s]"
                    % plugin_name
                )