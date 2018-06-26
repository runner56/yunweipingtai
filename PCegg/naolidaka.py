# -*- coding:utf-8 -*-
# -*- 微信小程序脑力大咖自动答题、抓取存储题目 -*-

import urllib, urllib2, requests
import time, json, hashlib, sys
import redisComponent

# 本人
userid = "10007465"
token = "i5lp2cs84sbdwwljcddzch1asj8hrpz29aah1frt"

# 惠清
# userid = "10021849"
# token = "kaw8cr54jc96qal57cs838ua8tzu11spagrafek9"

redisInstance = redisComponent.redisComponent()


def getUserInfo():
    """相当于登录，每日可获取一张挑战卡"""
    url = "https://ssl.rd88.com/IFS/Users/userinfo.ashx"
    data = {
        "userid":userid,
        "token":token
    }
    rsp = requests.get(url, params=data).json()
    userinfo = rsp["data"]["userinfo"][0]
    print u"%s，挑战次数：%s，挑战币：%s" % (userinfo["nickname"],str(userinfo["battlenum"]), str(userinfo["bmoney"]))


def setReserveId():
    url = "https://ssl.rd88.com/IFS/SetReserveid.ashx"
    data = {
        "userid":userid,
        "token":token,
        "reserveid":int(time.time()*1000)
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    print rsp.read().decode("utf8")

def zhQuestBegin():
    url = "https://ssl.rd88.com/IFS/Quests/zh_questbegin.ashx"
    data = {
        "userid":userid,
        "token":token
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    rspContent = json.loads(rsp.read())
    issueid = rspContent["data"]["issueid"]
    print issueid
    return issueid

def zhQuestShow(issueid, index):
    url = "https://ssl.rd88.com/IFS/Quests/zh_questshow.ashx"
    data = {
        "userid":userid,
        "token":token,
        "issueid":issueid,
        "indexmark":index
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    rspContent = rsp.read()
    try:
        print rspContent.decode("utf8")
    except UnicodeEncodeError:
        print u"UTF8解码出错？"

    rspContent = json.loads(rspContent) #json.loads得到的结果都是unicode编码的
    return rspContent

    


def zhQuestSubmit(issueid, index, submitanswer, quecontent):
    url = "https://ssl.rd88.com/IFS/Quests/zh_questsubmit.ashx"
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
    # print u"正确答案：%s" % rightanswer

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
    

def zhQuestOver():
    url = "https://ssl.rd88.com/IFS/Quests/zh_questover.ashx"
    data = {
        "userid": userid,
        "token": token,
        "issueid": issueid
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    print rsp.read().decode("utf8")


def tzQuestBegin():
    url = "https://ssl.rd88.com/IFS/Quests/tz_questbegin.ashx"
    data = {
        "userid":userid,
        "token":token
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    rspContent = json.loads(rsp.read())
    issueid = rspContent["data"]["issueid"]
    print issueid
    return issueid

def tzQuestShow(issueid, index):
    url = "https://ssl.rd88.com/IFS/Quests/tz_questshow.ashx"
    # url = "https://www.easy-mock.com/mock/5aa672f692ef6c5385609673/example/IFS/Quests/zh_questshow.ashx"
    data = {
        "userid":userid,
        "token":token,
        "issueid":issueid,
        "indexmark":index
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    rspContent = rsp.read()
    print rspContent.decode("utf8")
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
    print u"正确答案：%s" % rightanswer

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

def judgeAnswer(quecontent):
    questshow = quecontent["data"]["questshow"][0]
    quedetail = questshow["quedetail"]
    optiona = questshow["optiona"]
    optionb = questshow["optionb"]
    optionc = questshow["optionc"]
    optiond = questshow["optiond"]

    md5 = hashlib.md5()
    md5.update(quedetail.encode("utf8"))    # 得把unicode转为utf8才能转MD5
    key = md5.hexdigest()
    print u"问题MD5:%s" % key
    # import pdb;pdb.set_trace()

    # print key
    # print quedetail
    # print optiona
    # print optionb
    # print optionc
    # print optiond

    content = redisInstance.get(key)
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
            print u"key:%s\n，答案为0，出现异常！" % key
            
        print u"存在相同问题，key:%s\n问题：\n%s\n答案：%s" % (key, json.dumps(quecontent,ensure_ascii=False), answer)

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

def exchangeBattleNum():
    url = "https://ssl.rd88.com/IFS/Quests/ExchangeBattleNum.ashx"
    data = {
        "userid": userid,
        "token": token
    }
    rsp = urllib2.urlopen(url+"?"+urllib.urlencode(data))
    print rsp.read().decode("utf8")

if __name__ == '__main__':

    if len(sys.argv)==2 and sys.argv[1]=="tz":
        # import pdb;pdb.set_trace()
        setReserveId()
        issueid = tzQuestBegin()

        for i in range(1,7):
            quecontent = tzQuestShow(issueid, i)
            answer = judgeAnswer(quecontent)
            answer = input("answer:")
            tzQuestSubmit(issueid, i, answer, quecontent)
        tzQuestOver()
        getUserInfo()
    elif len(sys.argv)==2 and sys.argv[1]=="exchange":
        exchangeBattleNum()
        getUserInfo()
    else:
        getUserInfo() # 相当于登录，每日可获取一张挑战卡
        count = 1
        while count<500:
            print u"\n第%d次答题" % count
            setReserveId()
            issueid = zhQuestBegin()
            for i in range(1,7):
                quecontent = zhQuestShow(issueid, i)
                answer = judgeAnswer(quecontent)
                time.sleep(1)
                zhQuestSubmit(issueid, i, answer, quecontent)
            zhQuestOver()
            count += 1
