# -*- coding:utf-8 -*-

import logging
import random
import re
import threading
import time
import os
import codecs

__author__ = 'sweet'

pluginRoot = os.path.split(os.path.realpath(__file__))[0]
wodiConf = os.path.join(pluginRoot, '..', 'config', 'wodi.conf')


class PlayerInfo(object):
    def __init__(self):
        self.uin = ''  # 用户唯一标示
        self.id = 0  # 用户编号
        self.name = ''  # 用户昵称
        self.isUndercover = False  # 是否卧底
        self.word = ''  # 抽到的词语
        self.isOut = False  # 是否出局


class MsgDto(object):
    __slots__ = (
        'poll_type', 'from_uin', 'send_uin', 'msg_type', 'reply_ip', 'to_uin', 'content', 'raw_content')

    def __init__(self):
        self.from_uin = ''  # 群的uin
        self.send_uin = ''  # 发消息人的uin
        self.to_uin = ''
        self.content = ''


class StatusHandler(object):
    def __init__(self):
        self.status = 'undefined'

    def handle(self, game, msgDto):
        return False  # 退出


class StartStatus(StatusHandler):
    """
    <初始化阶段>
    """

    def __init__(self):
        super(StatusHandler, self).__init__()
        self.status = 'StartStatus'

    def handle(self, game, msgDto):
        content = msgDto.content
        matches = re.match(ur'.*谁是卧底((\d+)人局)?(.*(\d+)卧底)?', content)
        if matches:
            playCount = 5
            undercoverCount = 1
            if matches.group(2):
                playCount = max(3, int(matches.group(2)))  # 三个人以下就别玩了。。。
            if matches.group(4):
                undercoverCount = int(matches.group(4))
            game.writePublic(u"玩游戏啦：谁是卧底 %d 人局，想玩的快快加入~(输入 我要参加，加入游戏)" % playCount)
            game.statusHandle = ReadyStatus(game, playCount, undercoverCount)
            return True
        return False


class ReadyStatus(StatusHandler):
    """
    <准备阶段>
    公告游戏人数
    允许玩家加入游戏
    """

    def __init__(self, game, maxPlayerCount, undercoverCount=1):
        super(StatusHandler, self).__init__()
        self.status = 'ReadyStatus'
        self.__game = game
        self.__maxPlayerCount = maxPlayerCount
        self.__undercoverCount = undercoverCount
        self.__startNotifyThread()

    def handle(self, game, msgDto):
        matchSuccess = re.match(ur'^\s*我要参加\s*$', msgDto.content)
        if not matchSuccess:
            return False
        playerInfo = PlayerInfo()
        playerInfo.uin = msgDto.send_uin
        playerInfo.name = game.uin2name(msgDto.send_uin)
        if playerInfo.uin in [x.uin for x in game.playerList]:
            return False
        game.addPlayer(playerInfo)
        game.writePublic(u"%s 加入游戏，当前人数 %d/%d" % (playerInfo.name, len(game.playerList), self.__maxPlayerCount))
        if len(game.playerList) >= self.__maxPlayerCount:
            return self.next()
        return False

    def __startNotifyThread(self, timeout=80):
        def process(statusHandle, game, timeout):
            while statusHandle == game.statusHandle and timeout > 0:
                time.sleep(1)
                timeout -= 1
                if timeout <= 0:
                    statusHandle.next()  # 开始游戏
                    return
                if timeout % 20 == 0:
                    game.writePublic(u"要玩游戏的快加入啦，剩余%s秒。" % (timeout))
                    continue
            return

        thread = threading.Thread(target=process, args=(self, self.__game, timeout))
        thread.start()

    def next(self):
        """
        进入下一阶段
        """
        lock = self.__game.lock
        lock.acquire()
        try:
            if self.__game.statusHandle == self:
                self.__game.statusHandle = AssignRolesStatus(self.__game, self.__undercoverCount)
            return True
        finally:
            lock.release()


class AssignRolesStatus(StatusHandler):
    """
    <分配角色阶段>
    初始化用户身份信息
    """

    def __init__(self, game, undercoverCount=1):
        """
        :param undercoverCount: 卧底人数
        :return:
        """
        super(StatusHandler, self).__init__()
        self.status = 'AssignRolesStatus'
        self.__game = game
        self.__undercoverCount = undercoverCount
        self.__nextStatusHandle = None
        self.__assignRoles()

    def handle(self, game, msgDto):
        game.statusHandle = self.__nextStatusHandle
        return True

    def __assignRoles(self):
        game = self.__game
        playerCount = len(game.playerList)
        maxUndercover = len(game.playerList) // 3
        self.__undercoverCount = min(maxUndercover, self.__undercoverCount)
        if playerCount < 3 or self.__undercoverCount <= 0:
            game.writePublic("玩家过少，游戏结束")
            self.__nextStatusHandle = EndStatus()
            return True
        # 获取卧底词
        normalWord, specialWord = self.__extractWords()
        # 分配卧底身份
        for x in game.playerList:
            x.isUndercover = False
            x.word = normalWord
        while len([x for x in game.playerList if x.isUndercover]) < self.__undercoverCount:
            i = random.randint(0, len(game.playerList) - 1)
            game.playerList[i].isUndercover = True
            game.playerList[i].word = specialWord
        # 游戏信息
        playerNames = '\n'.join(['[%s号]%s' % (x.id, x.name) for x in game.playerList])
        game.writePublic(u"[%s]本次游戏共 %d 人，卧底 %d 人。玩家列表：\n%s\n\n我会私聊通知各玩家身份哦，记得查看!!~~" % (
            game.gameId, len(game.playerList), self.__undercoverCount, playerNames))
        # 私聊玩家，通知词语
        for x in game.playerList:
            game.writePrivate(x.uin, u'[%s]谁是卧底，您本局[%s]的词语是：%s' % (x.name,game.gameId, x.word))
        # 进入发言阶段
        self.__nextStatusHandle = SpeechStatus(self.__game)
        return True

    def __extractWords(self):
        """
        抽取平民词与卧底词
        :return:
        """
        with codecs.open(wodiConf, 'r', 'utf-8') as conf:
            lines = conf.readlines()
            lineNo = random.randint(0, len(lines) - 1)
            words = str(lines[lineNo]).replace('\n', '').split('----')
            if len(words) == 2:
                n = random.randint(0, 1)
                normalWord = words[n].strip()
                specialWord = words[1 - n].strip()
                return normalWord, specialWord
        return None, None


class SpeechStatus(StatusHandler):
    """
    <发言阶段>
    玩家依次发言
    """

    def __init__(self, game):
        super(StatusHandler, self).__init__()
        self.status = 'SpeechStatus'
        self.__game = game
        self._history = {}
        self._playerSet = {}
        self.__first()
        self.__startNotifyThread()

    def handle(self, game, msgDto):
        uin = msgDto.send_uin
        content = msgDto.content
        if uin not in self._playerSet:
            return False
        if uin not in self._history:
            self._history[uin] = content
        # 发言结果
        if len(self._history) >= len(self._playerSet):
            lst = [(u'[%s号]: %s' % (self._playerSet[uin], value)) for uin, value in self._history.items()]
            playerReplys = '\n'.join(lst)
            game.writePublic(u"发言结束：\n" + playerReplys)
            return self.next()
        return False

    def __first(self):
        game = self.__game
        lst = game.playerList
        for x in lst:
            self._playerSet[x.uin] = x.id
        i = random.randint(0, len(lst) - 1)
        playerInfo = lst[i]
        game.writePublic(u"发言阶段，请从%d号玩家[%s]开始，依次发言。" % (playerInfo.id, playerInfo.name))
        return

    def __startNotifyThread(self, timeout=80):
        def process(statusHandle, game, timeout):
            while statusHandle == game.statusHandle and timeout > 0:
                time.sleep(10)
                timeout -= 10
                if timeout <= 0:
                    statusHandle.next()  # 进行下一阶段
                    return
                if timeout % 20 == 0:
                    game.writePublic(u"还没有发言的玩家快发言啦，剩余%s秒。" % (timeout))
                    continue
            return

        thread = threading.Thread(target=process, args=(self, self.__game, timeout))
        thread.start()

    def next(self):
        """
        进入下一阶段
        """
        lock = self.__game.lock
        lock.acquire()
        try:
            if self.__game.statusHandle == self:
                self.__game.statusHandle = VoteStatus(self.__game)
            return True
        finally:
            lock.release()


class VoteStatus(StatusHandler):
    """
    <投票阶段>
    玩家投出代表自己的一票
    """

    def __init__(self, game):
        super(StatusHandler, self).__init__()
        self.status = 'VoteStatus'
        self.__game = game
        self._history = {}
        self._score = {}  # 投票结果
        self.__first()
        self.__startNotifyThread()

    def handle(self, game, msgDto):
        uin = msgDto.send_uin
        content = msgDto.content
        if uin not in self._playerSet:
            return False
        if uin not in self._history:
            matches = re.match(ur'.*(\d+)号*', content)
            if matches:
                id = int(matches.group(1))
                self._history[uin] = content
                if id not in self._score:
                    self._score[id] = 1
                else:
                    self._score[id] += 1
        # 投票结束
        if len(self._history) >= len(self._playerSet):
            return self.next()
        return False

    def __first(self):
        game = self.__game
        self._playerSet = set([x.uin for x in game.playerList if not x.isOut])
        game.writePublic(u"投票开始，请投卧底。")
        return

    def __startNotifyThread(self, timeout=80):
        def process(statusHandle, game, timeout):
            while statusHandle == game.statusHandle and timeout > 0:
                time.sleep(10)
                timeout -= 10
                if timeout <= 0:
                    statusHandle.next()  # 进行下一阶段
                    return
                if timeout % 20 == 0:
                    game.writePublic(u"快投票哇，剩余%s秒。" % (timeout))
                    continue
            return

        thread = threading.Thread(target=process, args=(self, self.__game, timeout))
        thread.start()

    def next(self):
        """
        进入下一阶段
        """
        lock = self.__game.lock
        lock.acquire()
        try:
            if self.__game.statusHandle == self:
                self.__game.statusHandle = VerdictStatus(self.__game, self._score)
            return True
        finally:
            lock.release()


class VerdictStatus(StatusHandler):
    """
    <裁决阶段>
    """

    def __init__(self, game, scoreDict):
        super(StatusHandler, self).__init__()
        self.status = 'VerdictStatus'
        self.__game = game
        self._score = scoreDict
        self.__nextStatusHandle = None
        self.__first()

    def handle(self, game, msgDto):
        game.statusHandle = self.__nextStatusHandle
        return True

    def __first(self):
        game = self.__game
        sortedScore = self.__getScore(game.playerList)
        msg = u'投票结果：\n'
        scoreList = '\t\n'.join([u'[%s号]: %s票' % (p.id, p.score) for p in sortedScore])
        outPlayer = sortedScore[0]
        p2 = sortedScore[1]
        # 平票
        if outPlayer.score == p2.score:
            game.writePublic(msg + scoreList + u'\n==== 平票！请继续发言 ====')
            self.__nextStatusHandle = SpeechStatus(game)
            return True
        # 玩家出局
        game.outPlayer(outPlayer.id)
        result = u'\n==== [%s号]%s 被投票出局 ====' % (outPlayer.id, outPlayer.name)
        game.writePublic(msg + scoreList + result)
        # 胜负判断
        undercoverCount = len([x for x in game.playerList if x.isUndercover])
        playerCount = len(game.playerList)
        if undercoverCount == 0:
            game.writePublic(u'==== 卧底出局，平民赢得胜利！！！ ====')
            self.__nextStatusHandle = EndStatus()
            return True
        elif playerCount == 2 or playerCount == undercoverCount:
            game.writePublic(u'==== 卧底获胜！！！ ====')
            self.__nextStatusHandle = EndStatus()
            return True
        self.__nextStatusHandle = SpeechStatus(game)
        return True

    def __getScore(self, playerList):
        keys = self._score.keys()
        for x in playerList:
            if x.id in keys:
                x.score = self._score[x.id]
            else:
                x.score = 0
        sortedScore = sorted(playerList, key=lambda x: x.score, reverse=True)
        return [x for x in sortedScore if x.score > 0]


class EndStatus(StatusHandler):
    """
    <结束阶段>
    """

    def __init__(self):
        super(StatusHandler, self).__init__()
        self.status = 'EndStatus'

    def handle(self, game, msgDto):
        game.statusHandle = StartStatus()
        return False


class Game(object):
    def __init__(self, statusHandle, groupHandler):
        self.statusHandle = statusHandle
        self.gameId = str(int(time.time()))[-5:]
        self.__playerList = []
        self._output = groupHandler
        self.lock = threading.Lock()

    @property
    def playerList(self):
        return tuple([x for x in self.__playerList if not x.isOut])

    @property
    def status(self):
        return self.statusHandle.status

    def addPlayer(self, playerInfo):
        playerInfo.id = len(self.__playerList) + 1
        self.__playerList.append(playerInfo)

    def outPlayer(self, id):
        """
        出局某玩家
        :param id: 玩家id
        :return:
        """
        for x in self.__playerList:
            if x.id == id:
                x.isOut = True
        pass

    def id2playerInfo(self, id):
        for x in self.playerList:
            if x.id == id:
                return x
        return None

    def writePublic(self, content):
        self._output.reply(content)
        time.sleep(0.5)
        pass

    def writePrivate(self, tuin, content):
        self._output.reply_sess(tuin, content)
        time.sleep(0.5)
        pass

    def uin2name(self, uin):
        """
        获取群成员信息，返回昵称
        :param uin:
        :return:str
        """
        lst = self._output.get_member_list()
        for x in lst:
            if str(x.uin) == str(uin):
                return x.nick
        return ""

    def run(self, msgDto):
        isProcess = False
        while self.statusHandle.handle(self, msgDto):
            isProcess = True
            pass
        return isProcess


# ===========================================================================================


if __name__ == "__main__":
    import sys

    reload(sys)
    sys.setdefaultencoding("utf-8")
    logging.basicConfig(level=logging.DEBUG)
    output = logging
    output.reply = logging.info
    output.reply_sess = lambda uin, msg: logging.info(msg)
    output.get_member_list = lambda: []

    # 开始5人局
    status = StartStatus()
    game = Game(status, output)
    msgDto = MsgDto()
    msgDto.content = u'!game 开始谁是卧底5人局2卧底'
    game.run(msgDto)

    # 报名
    game.run(MsgDto())
    msgDto1 = MsgDto()
    msgDto1.send_uin = '1'
    msgDto1.content = u'我要参加'
    game.run(msgDto1)
    msgDto2 = MsgDto()
    msgDto2.send_uin = '2'
    msgDto2.content = u'我要参加'
    game.run(msgDto2)
    msgDto3 = MsgDto()
    msgDto3.send_uin = '3'
    msgDto3.content = u'我要参加'
    game.run(msgDto3)
    msgDto4 = MsgDto()
    msgDto4.send_uin = '4'
    msgDto4.content = u'我要参加'
    game.run(msgDto4)
    msgDto5 = MsgDto()
    msgDto5.send_uin = '5'
    msgDto5.content = u'我要参加'
    game.run(msgDto5)

    # 发言
    msgDto1.content = u'发言1'
    game.run(msgDto1)
    msgDto2.content = u'发言2'
    game.run(msgDto2)
    msgDto3.content = u'发言3'
    game.run(msgDto3)
    msgDto4.content = u'发言4'
    game.run(msgDto4)
    msgDto5.content = u'发言5'
    game.run(msgDto5)

    # 投票
    msgDto1.content = u'1号'
    game.run(msgDto1)
    msgDto2.content = u'我投1号'
    game.run(msgDto2)
    msgDto3.content = u'2号是卧底'
    game.run(msgDto3)
    msgDto4.content = u'1'
    game.run(msgDto4)
    msgDto5.content = u'3号'
    game.run(msgDto5)
    threading.Event().set()

    # time.sleep(3)
