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
        matches = re.match(ur'.*开始谁是卧底((\d+)人局)?(.*(\d+)卧底)?', content)
        if matches:
            playCount = 5
            undercoverCount = 1
            if matches.group(2):
                playCount = int(matches.group(2))
            if matches.group(4):
                undercoverCount = int(matches.group(4))
            game.writePublic(u"玩游戏啦：谁是卧底 %d 人局，想玩的快快加入~(输入 我要参加，加入游戏)" % playCount)
            game.statusHandle = ReadyStatus(playCount, undercoverCount)
            return True
        return False


class ReadyStatus(StatusHandler):
    """
    <准备阶段>
    公告游戏人数
    允许玩家加入游戏
    """
    _playCount = 0
    _undercoverCount = 0

    def __init__(self, playCount, undercoverCount=1):
        super(StatusHandler, self).__init__()
        self.status = 'ReadyStatus'
        self._playCount = playCount
        self._undercoverCount = undercoverCount

    def handle(self, game, msgDto):
        matchSuccess = re.match(ur'^\s*我要参加.*\s*$', msgDto.content)
        if not matchSuccess:
            return False
        playerInfo = PlayerInfo()
        playerInfo.uin = msgDto.send_uin
        playerInfo.name = game.uin2name(msgDto.send_uin)
        if playerInfo.uin in [x.uin for x in game.playerList]:
            return False
        game.addPlayer(playerInfo)
        game.writePublic(u"%s 加入游戏，当前人数 %d/%d" % (playerInfo.name, len(game.playerList), self._playCount))
        if len(game.playerList) >= self._playCount:
            game.statusHandle = AssignRolesStatus(self._undercoverCount)
            return True
        return False


class AssignRolesStatus(StatusHandler):
    """
    <分配角色阶段>
    初始化用户身份信息
    """
    _undercoverCount = 0

    def __init__(self, undercoverCount=1):
        """
        :param undercoverCount: 卧底人数
        :return:
        """
        super(StatusHandler, self).__init__()
        self.status = 'AssignRolesStatus'
        self._undercoverCount = undercoverCount

    def handle(self, game, msgDto):
        maxUndercover = len(game.playerList) // 3
        self._undercoverCount = min(maxUndercover, self._undercoverCount)
        # 获取卧底词
        normalWord, specialWord = self.__extractWords()
        # 分配卧底身份
        for x in game.playerList:
            x.isUndercover = False
            x.word = normalWord
        while len([x for x in game.playerList if x.isUndercover]) < self._undercoverCount:
            i = random.randint(0, len(game.playerList) - 1)
            game.playerList[i].isUndercover = True
            game.playerList[i].word = specialWord
        # 游戏信息
        playerNames = ','.join([x.name for x in game.playerList])
        game.writePublic(u"[%s]本次游戏共 %d 人，卧底 %d 人。\n玩家列表：%s" % (
            game.gameId, len(game.playerList), self._undercoverCount, playerNames))
        # 私聊玩家，通知词语
        for x in game.playerList:
            game.writePrivate(x.uin, u'谁是卧底，您本局[%s]的词语是：%s' % (game.gameId, x.word))
        # 进入发言阶段
        game.statusHandle = SpeechStatus()
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

    def __init__(self, ):
        super(StatusHandler, self).__init__()
        self.status = 'SpeechStatus'
        self._history = {}
        self._first = True
        self._playerSet = set()

    def handle(self, game, msgDto):
        if self._first:
            self._first = False
            lst = game.playerList
            self._playerSet = {}
            for x in lst:
                self._playerSet[x.uin] = x.id
            i = random.randint(0, len(lst) - 1)
            playerInfo = lst[i]
            game.writePublic(u"发言阶段，请从%d号玩家[%s]开始，依次发言。" % (playerInfo.id, playerInfo.name))
            return
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
            game.statusHandle = VoteStatus()
            return True
        return False


class VoteStatus(StatusHandler):
    """
    <投票阶段>
    玩家投出代表自己的一票
    """

    def __init__(self, ):
        super(StatusHandler, self).__init__()
        self.status = 'VoteStatus'
        self._history = {}
        self._score = {}  # 投票结果
        self._first = True

    def handle(self, game, msgDto):
        if self._first:
            self._first = False
            self._playerSet = set([x.uin for x in game.playerList if not x.isOut])
            game.writePublic(u"投票开始，请投卧底。")
            return
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
            game.statusHandle = VerdictStatus(self._score)
            return True
        return False


class VerdictStatus(StatusHandler):
    """
    <裁决阶段>
    """

    def __init__(self, scoreDict):
        super(StatusHandler, self).__init__()
        self.status = 'VerdictStatus'
        self._score = scoreDict

    def handle(self, game, msgDto):
        sortedScore = self.__getScore()
        msg = u'投票结果：\n'
        scoreList = '\t\n'.join([u'[%s号]: %s票' % (p.id, p.score) for p in sortedScore])
        outPlayer = sortedScore[0]
        game.outPlayer(outPlayer.id)
        result = u'\n==== [%s号]%s 被投票出局 ====' % (outPlayer.id, outPlayer.name)
        game.writePublic(msg + scoreList + result)

        undercoverCount = len([x for x in game.playerList if x.isUndercover])
        playerCount = len(game.playerList)
        if undercoverCount == 0:
            game.writePublic(u'==== 卧底出局，平民赢得胜利！！！ ====')
            game.statusHandle = EndStatus()
            return True
        elif playerCount == 2 or playerCount == undercoverCount:
            game.writePublic(u'==== 卧底胜利！！！ ====')
            game.statusHandle = EndStatus()
            return True
        else:
            game.statusHandle = SpeechStatus()
            return True
        return False

    def __getScore(self):
        keys = self._score.keys()
        lst = game.playerList[:]
        for x in lst:
            if x.id in keys:
                x.score = self._score[x.id]
            else:
                x.score = 0
        sortedScore = sorted(lst, key=lambda x: x.score, reverse=True)
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
    def __init__(self, statusHandle, output):
        self.statusHandle = statusHandle
        self.gameId = str(int(time.time()))[-5:]
        self.__playerList = []
        self._output = output

    @property
    def playerList(self):
        return [x for x in self.__playerList if not x.isOut][:]

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
        pass

    def writePrivate(self, tuin, content):
        self.reply_sess(tuin, content)
        pass

    def uin2name(self, uin):
        return "name" + uin

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
    pub = logging
    pub.reply = logging.info

    # 开始5人局
    status = StartStatus()
    game = Game(status, pub, pri)
    msgDto = MsgDto()
    msgDto.content = u'!game 开始谁是卧底4人局2卧底'
    game.run(msgDto)

    # 报名
    game.run(MsgDto())
    msgDto1 = MsgDto()
    msgDto1.send_uin = '1'
    msgDto1.content = u'我要参加1'
    game.run(msgDto1)
    msgDto2 = MsgDto()
    msgDto2.send_uin = '2'
    msgDto2.content = u'我要参加2'
    game.run(msgDto2)
    msgDto3 = MsgDto()
    msgDto3.send_uin = '3'
    msgDto3.content = u'我要参加3'
    game.run(msgDto3)
    msgDto4 = MsgDto()
    msgDto4.send_uin = '4'
    msgDto4.content = u'我要参加4'
    game.run(msgDto4)
    # game.run(msgDto4)
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

    # time.sleep(3)
