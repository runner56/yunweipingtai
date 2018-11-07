# -*- coding:utf-8 -*-
# -*- 微信小程序脑力大咖自动答题、抓取存储题目 -*-

import os, sys, time, datetime,requests, hashlib, json
from threading import Thread, Timer
from redisComponent import redisComponent

sys.path.append("..")
import qywx, conf

class MsgManager(qywx.WxMsgSender):
    def __init__(self):
        super(MsgManager, self).__init__()
        self.msgList = []

    @classmethod
    def sendMsg(self, msg, msgType="text"):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        msg = u"{} {}".format(timeStr, msg)
        self.sendWxMsg(msg.replace("\"", u"“"), "text")

    @classmethod
    def appendMsgList(self, msg):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        msg     = u"{} {}".format(timeStr, msg)
        self.msgList.append(msg)

    @classmethod
    def sendMsgList(self, msgType="text"):
        msg = "\r\n".join([unicode(i) for i in self.msgList]) # 解决msgList出现None的问题
        self.sendWxMsg(msg.replace("\"", u"“"), "text")
        self.msgList = [] # 清空内容


class naolidakaThread(MsgManager, redisComponent, Thread):
    def __init__(self, userid, token):
        super(naolidakaThread, self).__init__()
        self.userid = userid
        self.token  = token
        self.nickname = ""
        self.todaystars = 0
        self.data   = {
                "userid": userid,
                "token" : token
        }

    def run(self):
        try:
            todaystatus = 0
            exchangestatus = 0
            self.getUserInfo() # 每日签到
            while todaystatus==0:
                self.setReserveId()
                issueid = self.zhQuestBegin()
                for i in range(1,7):
                    questcontent = self.zhQuestShow(issueid, i)
                    answer = self.judgeAnswer(questcontent)
                    time.sleep(1)
                    self.zhQuestSubmit(issueid, i, answer, questcontent)
                zhQuestOverRsp = self.zhQuestOver(issueid) # 答题次数达到上限后就跳出循环
                todaystatus = zhQuestOverRsp["data"]["todaystatus"]
                if todaystatus==0:
                    self.todaystars += zhQuestOverRsp["data"]["wstars"]
                    self.sendMsg(u"{nickname},获得{wstars}星,当天总计获得{todaystars}星,现有{starnum}".format(
                            nickname = self.nickname,
                            wstars = zhQuestOverRsp["data"]["wstars"],
                            todaystars = self.todaystars,
                            starnum = zhQuestOverRsp["data"]["starnum"],
                        ))

            while exchangestatus==0:
                time.sleep(1)
                exchangestatus = self.exchangeBattleNum()
        
        except:
            import traceback
            msg = traceback.format_exc().decode("utf8")
            self.sendMsg(msg)

    def getUserInfo(self):
        """相当于登录，每日可获取一张挑战卡"""
        url = "https://ssl.rd88.com/IFS/Users/userinfo.ashx"
        rsp = requests.get(url, params=self.data).json()
        userinfo = rsp["data"]["userinfo"][0]
        self.nickname = userinfo["nickname"]
        msg = u"{nickname}, 星星:{starnum}, 挑战次数:{battlenum}, 挑战币:{bmoney}".format(**userinfo)
        self.sendMsg(msg)

    def setReserveId(self):
        """点击进入答题"""
        url = "https://ssl.rd88.com/IFS/SetReserveid.ashx"
        data = self.data.copy()
        data["reserveid"] = int(time.time()*1000)
        requests.get(url, params=data)
        # rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        # print rsp.read().decode("utf8")

    def zhQuestBegin(self):
        url = "https://ssl.rd88.com/IFS/Quests/zh_questbegin.ashx"
        rsp = requests.get(url, params=self.data).json()
        issueid = rsp["data"]["issueid"]
        return issueid

    def zhQuestShow(self, issueid, index):
        url = "https://ssl.rd88.com/IFS/Quests/zh_questshow.ashx"
        data = self.data.copy()
        data["issueid"] = issueid
        data["indexmark"] = index
        rsp = requests.get(url, params=data).json()
        questshow = rsp["data"]["questshow"][0]
        questcontent = {
            "issueid": questshow["issueid"],
            "quedetail":questshow["quedetail"],
            "optiona":questshow["optiona"],
            "optionb":questshow["optionb"],
            "optionc":questshow["optionc"],
            "optiond":questshow["optiond"],
        }
        return questcontent

    def zhQuestSubmit(self, issueid, index, submitanswer, questcontent):
        url = "https://ssl.rd88.com/IFS/Quests/zh_questsubmit.ashx"
        data = self.data.copy()
        data["issueid"] = issueid
        data["indexmark"] = index
        data["submitanswer"] = submitanswer
        rsp = requests.get(url, params=data).json()
        # rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        # rspContent = json.loads(rsp.read()) #json.loads得到的结果都是unicode编码的
        rightanswer = rsp["data"]["rightanswer"] # 是int类型，不需要转为unicode
        # print u"正确答案：%s" % rightanswer

        quedetail = questcontent["quedetail"]
        optiona = questcontent["optiona"]
        optionb = questcontent["optionb"]
        optionc = questcontent["optionc"]
        optiond = questcontent["optiond"]

        md5 = hashlib.md5()
        md5.update(quedetail.encode("utf8"))    # 得把unicode转为utf8才能转MD5
        key = md5.hexdigest()
        value = {
            "quedetail": quedetail,
            "optiona": optiona,
            "optionb": optionb,
            "optionc": optionc,
            "optiond": optiond,
            "rightanswer": rightanswer
        }
        self.save(key, json.dumps(value,ensure_ascii=False))
        
    def zhQuestOver(self, issueid):
        url = "https://ssl.rd88.com/IFS/Quests/zh_questover.ashx"
        data = self.data.copy()
        data["issueid"] = issueid
        rsp = requests.get(url, params=data).json()
        return rsp

    def tzQuestBegin():
        url = "https://ssl.rd88.com/IFS/Quests/tz_questbegin.ashx"
        data = {
            "userid":userid,
            "token":token
        }
        rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        rspContent = json.loads(rsp.read())
        issueid = rspContent["data"]["issueid"]
        return issueid

    def tzQuestShow(issueid, index):
        url = "https://ssl.rd88.com/IFS/Quests/tz_questshow.ashx"
        data = {
            "userid":userid,
            "token":token,
            "issueid":issueid,
            "indexmark":index
        }
        rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        rspContent = rsp.read()
        rspContent = json.loads(rspContent) #json.loads得到的结果都是unicode编码的
        return rspContent

    def tzQuestSubmit(issueid, index, submitanswer, quecontent):
        url = "https://ssl.rd88.com/IFS/Quests/tz_questsubmit.ashx"
        data = {
            "userid":userid,
            "token":token,
            "issueid":issueid,
            "indexmark":index,
            "submitanswer":submitanswer
        }
        rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        rspContent = json.loads(rsp.read()) #json.loads得到的结果都是unicode编码的
        rightanswer = rspContent["data"]["rightanswer"] # 是int类型，不需要转为unicode
        questshow = quecontent["data"]["questshow"][0]
        quedetail = questshow["quedetail"]
        optiona = questshow["optiona"]
        optionb = questshow["optionb"]
        optionc = questshow["optionc"]
        optiond = questshow["optiond"]

        md5 = hashlib.md5()
        md5.update(quedetail.encode("utf8"))    # 得把unicode转为utf8才能转MD5
        key = md5.hexdigest()
        value = {
            "quedetail": quedetail,
            "optiona": optiona,
            "optionb": optionb,
            "optionc": optionc,
            "optiond": optiond,
            "rightanswer": rightanswer
        }
        redisInstance.save(key, json.dumps(value,ensure_ascii=False))
        
    def tzQuestOver():
        url = "https://ssl.rd88.com/IFS/Quests/tz_questover.ashx"
        data = {
            "userid": userid,
            "token": token,
            "issueid": issueid
        }
        rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
        print rsp.read().decode("utf8")

    def judgeAnswer(self, questcontent):
        quedetail = questcontent["quedetail"]
        optiona = questcontent["optiona"]
        optionb = questcontent["optionb"]
        optionc = questcontent["optionc"]
        optiond = questcontent["optiond"]

        md5 = hashlib.md5()
        md5.update(quedetail.encode("utf8"))    # 得把unicode转为utf8才能转MD5
        key = md5.hexdigest()

        content = self.get(key)
        if content:
            content = json.loads(content)
            answerIndex = content["rightanswer"]
            if answerIndex==1:
                answer = content["optiona"]
            elif answerIndex==2:
                answer = content["optionb"]
            elif answerIndex==3:
                answer = content["optionc"]
            elif answerIndex==4:
                answer = content["optiond"]
            else:
                answer = 0
                # self.sendMsg(u"key:%s\n，答案为0，出现异常！" % key)
                
            # self.sendMsg(u"存在相同问题，key:%s\n问题：\n%s\n答案：%s" % (key, json.dumps(questcontent,ensure_ascii=False), answer))

            if optiona==answer:
                return 1
            elif optionb==answer:
                return 2
            elif optionc==answer:
                return 3
            elif optiond==answer:
                return 4
            else:
                return 2
        else:
            return 2

    def exchangeBattleNum(self):
        url = "https://ssl.rd88.com/IFS/Quests/ExchangeBattleNum.ashx"
        data = {
            "userid": self.userid,
            "token": self.token
        }
        rsp = requests.get(url, params=data).json()
        self.sendMsg(rsp["msg"])
        return rsp["status"]


userDict = [{
        "userid":"10007465",    # 本人
        "token":"i5lp2cs84sbdwwljcddzch1asj8hrpz29aah1frt"
        },{
        "userid":"10021849",    # 惠清
        "token":"kaw8cr54jc96qal57cs838ua8tzu11spagrafek9"
        },{
        "userid":"10062246",    # 妈
        "token":"rtzktrsuze7891r8rrs91puu8u46cpcguc377bpt"
        }]

def getTimeDelta():
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=8)
    delta = tom1-now
    return delta.total_seconds() # 转化为秒

def main():
    for user in userDict:
        t = naolidakaThread(user["userid"], user["token"])
        # t.setDaemon(True)
        t.start()
    timedelta = getTimeDelta()
    Timer(timedelta, main).start()

if __name__ == "__main__":
    
    try:
        # timedelta = getTimeDelta()  # 得当前时间至明天8点的秒数(浮点)
        # Timer(timedelta, main).start()  # main没有参数，Timer就不用加参数三了
        main()
    except:
        import traceback
        msg = traceback.format_exc().decode("utf8")
        MsgManager.sendMsg(msg)

