import time, threading, hashlib, requests, json, urllib

import logging
logger = logging.getLogger(__name__)

class app(object):
    APP_FROM = 2
    RQ_ACT_ENROLL = "act_clockin_enroll.ashx"  # 应该改为小写
    RQ_ACT_CLOCKIN = "Act_ClockIn_TodayIssue.ashx".lower()
    RQ_ACT_CLOCKIN_CLOCKIN = "Act_ClockIn_ClockIn.ashx".lower()
    APP_KEY = "3Grzq#7Pir9c5Cw^b#"

    __getArticleListUrl = "http://games.q9x9.com/app_information_flow/article/queryArticleList" #userId=27332503&pageNo=1
    __openArticleUrl = "http://games.q9x9.com/app_information_flow/article/queryShareMsg" #userId=27332503&articleId=1275
    __getGoldMoneyUrl = "http://games.q9x9.com/app_information_flow/article/addUserArticleGoldMoney" #userId=27332503&articleId=1275&type=2

    def __init__(self, user, userid, noveluserid, deviceid, token, *args, **kwargs):
        self.user = user
        self.userid = userid
        self.noveluserid = noveluserid
        self.deviceid = deviceid
        self.token = token
        self.novelGoldcoin = 0
        self.stroageDict = {
            "totalGolds": 0,
            "content": None,
            "index": 0,
            "articleGolds": 0,
            "articleTye": 0,
            "articleId": None,
        }   # 用于阅读文章时储存信息

    @staticmethod
    def encry(s):
        m = hashlib.md5()
        m.update(s)
        o = m.digest()
        a = b'0123456789abcdef'
        i = 0
        cArr = []
        while(i<len(o)):
            b = o[i]
            cArr.append(a[(b>>4) & 15])
            cArr.append(a[b & 15])
            i += 1
        return "".join([chr(i) for i in cArr])

    @classmethod
    def getSalt(self, st):
        lt = time.localtime(st)    
        ft = time.strftime('%Y%m%d', lt)
        day = int(time.strftime('%d', lt))
        i = 0
        d = 20
        c = "哈哈哈哈，总算给你找到了，很难找吧，赚几个钱不容易吧，可惜这里还不是全部，再接再厉，继续找找！"  # 47个字符
        o = []
        if d+day>len(c):
            length = d+day-len(c)
            while i<length:
                o.append(c[i])
                i += 1
            while day<len(c):
                o.append(c[day])
                day += 1
        else:
            while i < d:
                o.append(c[day - 1 + i])    # 29日，29-1+19=47，出现序号大于列表长度的情况？
                i += 1
        a = "".join(o) + ft
        s = self.encry(a.encode('utf8'))
        return s

    def readADReward(self):
        """
        阅读小说，获取奖励
        """
        url = "http://www.ipadview.com/rpads/score/award"
        productId = '8246'
        bookId = 0
        chapterId = 0
        st = time.time()
        salt = self.getSalt(st)
        x = str(self.noveluserid)+str(productId)+str(self.deviceid)+salt+str(round(st*1000))
        cs = self.encry(x.encode("utf8"))
        payload = {
            "st": round(st*1000),
            "productId": productId,
            "bookChannel": 1,
            "userId": self.noveluserid,
            "bookName": "闯关默认书名",
            "bookId": bookId,
            "cs":cs,
            "chapterId": chapterId,
            "imei": self.deviceid,
            "readType": 1,
            "projectId": 67,
            "bookType": 0 ,
            "doTask": 1, #这个参数不能少
            "adDurations": 15,
            "adClickCounts": 2,
            "adSource": "wangxingJS",
        }
        header = {
            "User-Agent": "Mozilla/5.0",
            "info-source": "sdk", # 这个参数不能少
        }
        r = requests.post(url, headers=header, data=payload)
        rsp = r.content.decode('utf8')
        logger.debug(rsp)
        try:
            rsp_json = json.loads(rsp)
        except:
            logger.critical("%s 解析返回值出错！", self.user)
            return False
        if rsp_json.get("code")!='0':
            logger.error("%s 返回值code不为0", self.user)
            return False

        try:
            score = rsp_json["data"]["score"]
        except:
            logger.error("%s 无法获取score", self.user)
            return False

        if score > 0:
            logger.debug("%s 奖励%d金币", self.user, score)
            self.novelGoldcoin += score
            return True
        
        if score == -60:
            logger.debug("%s 开启小说免费阅读", self.user)
            return True

        logger.error("%s 返回值score值为%d，已经获取完", self.user, score)
        return False

    def _generate_keycode(self, st, urlcode): # 不能加使用classmethod，类实例可以调用它，但它无法调用类实例属性
        content = str(self.APP_FROM) + str(self.deviceid) + str(self.userid) + self.token + str(st) + urlcode + self.APP_KEY
        m = hashlib.md5()
        m.update(content.encode("utf8"))
        keycode = m.hexdigest()
        return keycode

    def clockEnroll(self, paymoney):
        """
        发起早起打卡
        """
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_Enroll.ashx"
        st = int(time.time()*1000)
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_ENROLL),
            'paymoney': paymoney,
            'isvideo': 1,
            'userid': self.userid,
            'paytype': 1,
            'payorder': "",
            'unix': st,
            'token': self.token
        }

        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceid, # 不能少
        }
        r = requests.post(url, headers=header, data=payload)
        logger.info(urllib.parse.unquote(r.content.decode("utf8")))

    def clockIn(self):
        """
        早起打卡
        """
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_ClockIn.ashx"
        st = int(time.time()*1000)
        cid = self.__getcid()
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_CLOCKIN_CLOCKIN),
            'userid': self.userid,
            'unix': st,
            'token': self.token,
            'cid': cid
        }

        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceid, # 不能少
        }
        r = requests.post(url, headers=header, data=payload)
        logger.info(urllib.parse.unquote(r.content.decode("utf8")))

    def __getcid(self):
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_TodayIssue.ashx"
        st = int(time.time()*1000)
        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceid, # 不能少
        }
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_CLOCKIN),
            'userid': self.userid,
            'unix': st,
            'token': self.token
        }
        r = requests.post(url, headers=header, data=payload)
        logger.debug(r.content.decode("utf8"))
        cid  = json.loads(r.content)['data']['items'][0]['cid']
        return cid

    def getArticleList(self):
        """
        获取文章列表
        """
        while True:
            try:
                rsp = requests.get(self.__getArticleListUrl, params={"userId":self.userid,"pageNo":"1"})
                logger.debug("%s 获取文章列表", self.user)
                break
            except requests.exceptions.ConnectionError:
                logger.error("%s 获取文章列表出错，3秒后再次重试！", self.user)
                time.sleep(3)
                continue
        ct = json.loads(rsp.content)
        self.stroageDict["content"] = ct
        self.stroageDict["index"] = 0
        self.stroageDict["articleGolds"] = 0

    def getArticle(self):
        if self.stroageDict.get("content") is None:
            self.getArticleList()
        datas = self.stroageDict.get("content").get("datas")
        i = self.stroageDict.get("index")
        if i < len(datas):
            article = datas[i]
            self.stroageDict["articleGolds"] = 0
            self.stroageDict["articleId"] = article.get("id")
            self.stroageDict["articleType"] = article.get("articleType")
            self.stroageDict["index"] = i+1
        else:
            self.getArticleList()
            self.getArticle()

    def getArticleReward(self):
        if self.stroageDict.get("articleId") is None:
            self.getArticle()
        articleId = self.stroageDict.get("articleId")
        articleType = self.stroageDict.get("articleType")
        rsp = requests.get(self.__getGoldMoneyUrl, params={"userId":self.userid, "articleId":articleId, "type":articleType})
        logger.debug(rsp.content.decode("utf8"))
        try:
            rsp_json = json.loads(rsp.content)
        except:
            logger.critical("%s 解析返回值出错！", self.user)
            return False

        msg = rsp_json.get("msg")

        if msg.find("查询成功")>-1:
            self.stroageDict["articleGolds"] += 500
            self.stroageDict["totalGolds"] += 500
            logger.debug("%s，文章%s %d，总获取%d",
                self.user,
                articleId,
                self.stroageDict["articleGolds"],
                self.stroageDict["totalGolds"],
            )
            if self.stroageDict["articleGolds"]==1500:
                logger.debug("%s 文章%s已获得1500金币，换个文章继续读。", self.user, articleId)
                self.getArticle()
            return True

        if msg.find("这篇文章您已阅读好久")>-1:
            logger.debug("%s，单篇文章%s阅读达上限", self.user, articleId)
            self.getArticle()
            return True

        if msg.find("奖励已到上限")>-1:
            logger.debug("%s，单日总奖励已达上限", self.user)
            return False

class readNovelThread(threading.Thread):
    def __init__(self, app):
        super(readNovelThread, self).__init__()
        self.app = app
    def run(self):
        logger.info("启动用户%s的阅读小说线程", self.app.user)
        count = 3
        while count > 0:
            flag = self.app.readADReward()
            if flag is False: count -= 1
            time.sleep(10)
        logger.info("阅读小说线程结束！%s 总共获得%d金币", self.app.user, self.app.novelGoldcoin)

class readArticleThread(threading.Thread):
    def __init__(self, app):
        super(readArticleThread, self).__init__()
        self.app = app
    def run(self):
        logger.info("启动用户%s的阅读新闻线程", self.app.user)
        count = 3
        while count > 0:
            flag = self.app.getArticleReward()
            if flag is False: count -= 1
            time.sleep(30)
        logger.info("阅读新闻线程结束！%s 总共获得%d金币", self.app.user, self.app.stroageDict.get("totalGolds"))
