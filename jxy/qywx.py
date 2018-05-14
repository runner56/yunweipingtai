#-*- coding:utf8 -*-
import requests, time


class WxMsgSender(object):
    def __init__(self):
        self.url = "http://127.0.0.1:7001/"

    def sendWxMsg(self, msg, type):
        """
            type:text/image
            msg: text类型时为文本，image类型时为文件路径
        """
        url = self.url + "sendMsg"
        requests.post(url, data={
                                "msg": msg,
                                "type":type
        })

    def getYZM(self):
        url = self.url + "getYZM"
        return requests.get(url).json()


class MsgManager(WxMsgSender):
    def __init__(self, account):
        super(MsgManager, self).__init__()
        self.account    = account
        self.uCoin      = ""
        self.keys       = []
        self.hoes       = []
        self.msgList    = []

    def fillParam(self, **kw):
        for k,v in kw.items():
            try:
                self.param[k] = v
            except KeyError:
                print "ERROR: NoSuchKey %s" % k


    def processMsg(self, msg, msgType="text"):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        if msgType=="image":
            self.sendWxMsg(msg, msgType)
        elif msgType=="text":
            msg = u"{} {}".format(timeStr, msg)
            self.msgList.append(msg)
            print msg
        else:
            raise ValueError

    def directTransMsg(self, msg, msgType="text"):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        msg = u"{} {}".format(timeStr, msg)
        self.sendWxMsg(msg, msgType)

    def sendTextMsg(self):
        self.msgList.insert(0, u"账号：%s" % self.uCoin)
        self.msgList.append(self.account)
        self.msgList.append(u"钥匙: %s" % ",".join(self.keys))
        self.msgList.append(u"锄头: %s" % ",".join(self.hoes))
        msg = "\r\n".join(self.msgList)
        self.sendWxMsg(msg, "text")
        # 清空内容
        self.uCoin      = ""
        self.keys       = []
        self.hoes       = []
        self.msgList    = []