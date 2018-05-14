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
    def __init__(self):
        super(MsgManager, self).__init__()

    def sendMsg(self, msg, msgType):
        print msg, msgType
        # self.sendWxMsg(msg, msgType)

    def getYZM(self):
        yzmCode = raw_input(u"请输入验证码：".encode("gbk"))
        return yzmCode