# coding: utf-8


class MsgProxyNotImplementError(ValueError):
    pass


class InvalidHandlerType(ValueError):
    pass


class ConfigFileDoesNotExist(IOError):
    pass


class ConfigKeyError(ValueError):
    pass


class ServerResponseEmpty(IOError):
    pass

class NeedRelogin(SystemExit):
    pass