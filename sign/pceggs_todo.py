# -*- coding:utf8 -*-

import os, sys, time, threading, random, datetime, hashlib, requests, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image

sys.path.append("..")
from conf import PCEGGS_ACCOUNTS
import logging
logger = logging.getLogger("makemoney.main.pceggs")

class web(object):
    __path = os.getcwd()

    def __init__(self, driver, msgManager):
        self.driver     = driver
        self.msgManager = msgManager
        # self.emailApi   = emailApi()

    def __call__(self):
        for account in PCEGGS_ACCOUNTS:
            user = account["user"]
            pwd = account["pwd"]
            try:
                self.__login(user, pwd)
                self.__sign()
            except:
                import traceback
                logger.critical(traceback.format_exc())
                # self.msgManager.sendMsg(traceback.format_exc().decode("utf8"), "text")
                # 必须进行utf8解码，要不然注释的中文是utf8编码的。在后面用replace会出现编码错误。
            self.__flushcookie()

    def __login(self, user, pwd):
        url = "http://www.pceggs.com/nologin.aspx"
        self.driver.get(url)
        loginBtnLocator = (By.ID, "Login_Submit")
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(loginBtnLocator))
        except TimeoutException:
            raise Exception("PCeggs:无法定位到登录按钮！")
        else:
            self.__input_login_info(user, pwd)

    def __input_login_info(self, user, pwd): # 输错验证码后可以再次输入，不必刷新页面
        loginMsgLocator = (By.ID, "div_msg") # 登录信息提示框，比如验证码错误
        yzmElement      = self.driver.find_element_by_id("valiCode")
        yzmElement.click()
        try:
            self.__sendYZM(yzmElement)  # 发送图片失败，再发送一次
        except:
            logger.error("发送验证码图片失败，尝试再次发送！")
            self.__input_login_info(user, pwd)
            return
        yzm = self.__getYZM()
        self.driver.find_element_by_id("txt_UserName").send_keys(user)
        self.driver.find_element_by_id("txt_PWD").send_keys(pwd)
        self.driver.find_element_by_id("txt_VerifyCode").send_keys(yzm)
        self.driver.find_element_by_id("Login_Submit").click()
        try:
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(loginMsgLocator))
        except TimeoutException:
            pass
        else:
            self.__input_login_info(user, pwd)

    def __sign(self):
        signBtnLocator = (By.XPATH, "//a[contains(text(),'\xe4\xbb\x8a\xe6\x97\xa5\xe7\xad\xbe\xe5\x88\xb0')]") #这里最好输入编码，今日签到转为utf8
        url = "http://www.pceggs.com/signIn/signIn.aspx"
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(signBtnLocator))
            self.driver.get(url)
        except TimeoutException:
            raise Exception("PCeggs:未定位到主页标识，可能已完成签到!")
        else:
            signDivLocator = (By.XPATH, "//div[contains(text(),'立即签到')]")
            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(signDivLocator))
            except TimeoutException:
                raise Exception("PCeggs:签到失败，未定位到签到按钮!")
            else:
                self.driver.execute_script("document.getElementsByClassName('anniu')[0].click()") # 通过js来调用点击，防止被遮挡
                # self.driver.find_element(*signDivLocator).click()
        finally:
            time.sleep(2)
            self.__screenshot()

    def __sendYZM(self, yzmElement):
        self.driver.save_screenshot("pceggsLogin.png")
        time.sleep(1)
        left = int(yzmElement.location["x"])
        top = int(yzmElement.location["y"])
        right = int(yzmElement.location["x"]+yzmElement.size["width"])
        bottom = int(yzmElement.location["y"]+yzmElement.size["height"])
        im = Image.open("pceggsLogin.png")
        im = im.crop((left, top, right, bottom))
        im.save("pceggsYZM.png")
        logger.info("sendImage:" + os.path.join(self.__path, "pceggsYZM.png"))
        logger.info("PCeggs:输入验证码,格式:@+验证码")
        # self.msgManager.sendMsg(os.path.join(self.__path, "pceggsYZM.png"), "image")
        # self.msgManager.sendMsg(u"PCeggs:输入验证码,格式:@+验证码", "text")

    def __getYZM(self):
        while True:
            time.sleep(8)
            yzm = self.msgManager.getYZM()
            # if yzm in [None,""]:
                # yzm = self.emailApi.recvEmail()
            if yzm:
                print(yzm)
                break
        logger.info(u"PCeggs:输入的验证码: %s", yzm)
        return yzm

    def __screenshot(self):
        self.driver.execute_script("window.scrollTo(1000,0)")
        self.driver.save_screenshot("pceggs.png")
        self.msgManager.sendMsg(os.path.join(self.__path, "pceggs.png"), "image")

    def __flushcookie(self):
        self.driver.delete_all_cookies()

class app(object):
    APP_FROM = 2
    RQ_ACT_ENROLL = "act_clockin_enroll.ashx"  # 应该改为小写
    RQ_ACT_CLOCKIN = "Act_ClockIn_TodayIssue.ashx".lower()
    RQ_ACT_CLOCKIN_CLOCKIN = "Act_ClockIn_ClockIn.ashx".lower()
    APP_KEY = "3Grzq#7Pir9c5Cw^b#"

    def __init__(self, user, userID, deviceID, token):
        self.user = user
        self.userID = userID
        self.deviceID = deviceID
        self.token = token
        self.novelGoldcoin = 0

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
        url = "http://www.ipadview.com/rpads/score/award"
        productId = '8246'
        bookId = 0
        chapterId = 0
        st = time.time()
        salt = self.getSalt(st)
        x = str(self.userID)+str(productId)+str(self.deviceID)+salt+str(round(st*1000))
        cs = self.encry(x.encode("utf8"))
        payload = {
            "st": round(st*1000),
            "productId": productId,
            "bookChannel": 1,
            "userId": self.userID,
            "bookName": "闯关默认书名",
            "bookId": bookId,
            "cs":cs,
            "chapterId": chapterId,
            "imei": self.deviceID,
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
            logger.critical("解析返回值出错！")
            return False
        if rsp_json.get("code")=='0':
            if rsp_json["data"]["score"]==500:
                logger.info("%s 奖励金币+500", self.user)
                self.novelGoldcoin += 500
                return True
            elif rsp_json["data"]["score"]==288:
                logger.info("%s 奖励金币+288", self.user)
                self.novelGoldcoin += 288
                return True
            elif rsp_json["data"]["score"]==-60:
                logger.info("%s 开启小说免费阅读", self.user)
                return True
            elif rsp_json["data"]["score"]==-80:
                logger.info("%s 今日小说金币已经获取完", self.user)
                return False
            else:
                logger.info("%s 阅读小说返回代码异常", self.user)
                return False
        else:
            logger.error("返回值code不为0")
            return False

    def _generate_keycode(self, st, urlcode): # 不能加使用classmethod，类实例可以调用它，但它无法调用类实例属性
        content = str(self.APP_FROM) + str(self.deviceID) + str(self.userID) + self.token + str(st) + urlcode + self.APP_KEY
        m = hashlib.md5()
        m.update(content.encode("utf8"))
        keycode = m.hexdigest()
        return keycode

    def clockEnroll(self, paymoney):
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_Enroll.ashx"
        st = int(time.time()*1000)
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_ENROLL),
            'paymoney': paymoney,
            'isvideo': 1,
            'userid': self.userID,
            'paytype': 1,
            'payorder': "",
            'unix': st,
            'token': self.token
        }

        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceID, # 不能少
        }
        r = requests.post(url, headers=header, data=payload)
        logger.debug(r.content.decode("utf8"))

    def clockIn(self):
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_ClockIn.ashx"
        st = int(time.time()*1000)
        cid = self.__getcid()
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_CLOCKIN_CLOCKIN),
            'userid': self.userID,
            'unix': st,
            'token': self.token,
            'cid': cid
        }

        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceID, # 不能少
        }
        r = requests.post(url, headers=header, data=payload)
        logger.debug(r.content.decode("utf8"))

    def __getcid(self):
        url = "http://ifsapp.pceggs.com/IFS/Activity/ClockIn/Act_ClockIn_TodayIssue.ashx"
        st = int(time.time()*1000)
        header = {
            'ptype': '2', # 不能少
            'deviceid': self.deviceID, # 不能少
        }
        payload = {
            'keycode': self._generate_keycode(st, self.RQ_ACT_CLOCKIN),
            'userid': self.userID,
            'unix': st,
            'token': self.token
        }
        r = requests.post(url, headers=header, data=payload)
        logger.debug(r.content.decode("utf8"))
        cid  = json.loads(r.content)['data']['items'][0]['cid']
        return cid

class readNovelThread(threading.Thread):
    def __init__(self, app):
        super(readNovelThread, self).__init__()
        self.app = app
    def run(self):
        flag = True
        while  flag:
            flag = self.app.readADReward()
            time.sleep(10)
        logger.info("%s 总共获得%d金币", self.app.user, self.app.novelGoldcoin)
        logger.info("阅读小说线程结束！")

def readNovel():
    for account in PCEGGS_ACCOUNTS:
        user = account["user"]
        userID = account["noveluserid"]
        deviceID = account["deviceid"]
        token = account["token"]
        readNovelThread(app(user, userID, deviceID, token)).start()

def clockIn():
    for account in PCEGGS_ACCOUNTS:
        user = account["user"]
        userID = account["userid"]
        deviceID = account["deviceid"]
        token = account["token"]
        app(user, userID, deviceID, token).clockIn()

def clockEnroll(paymoney):
    for account in PCEGGS_ACCOUNTS:
        user = account["user"]
        userID = account["userid"]
        deviceID = account["deviceid"]
        token = account["token"]
        app(user, userID, deviceID, token).clockEnroll(paymoney)

