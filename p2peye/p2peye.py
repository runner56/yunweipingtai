# -*- coding:utf8 -*-

import os, sys, time, threading, random, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image

sys.path.append("..")
from conf import P2PEYE_Conf 
from emailapi import emailApi
if len(sys.argv)>1 and sys.argv[1]=="test":
    from qywx import TestMsgManager as MsgManager
else:
    from qywx import MsgManager

# PATH = os.getcwd() # 当前目录，用于存储验证码图片
ACCOUNTS = P2PEYE_Conf["ACCOUNTS"]
driverList = []
PATH = os.getcwd() # 当前目录，用于存储验证码图片

# 初始化
def initialDriver(msgManger):
    timeStr = time.strftime("%H:%M:%S", time.localtime())
    msgManger.sendMsg(u"{} {}".format(timeStr, u"P2P天眼：初始化浏览器！"), "text")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--proxy-server=socks5://localhost:7001")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

class p2peye(object):
    def __init__(self, driver, user, pwd, msgManger):
        self.driver    = driver
        self.user      = user
        self.pwd       = pwd
        self.msgManger = msgManger
        self.msgList   = []
        self.emailApi  = emailApi()

    # 把msgManger都封装了一遍
    def sendMsg(self, msg, msgType="text"):
        if msgType=="text":
            timeStr = time.strftime("%H:%M:%S", time.localtime())
            msg = u"{} {}".format(timeStr, msg)
        self.msgManger.sendMsg(msg, msgType)

    def appendMsgList(self, msg):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        msg = u"{} {}".format(timeStr, msg)
        self.msgList.append(msg)

    def sendMsgList(self, msgType="text"):
        msg = "\r\n".join([unicode(i) for i in self.msgList]) # 解决msgList出现None的问题
        self.msgManger.sendMsg(msg, "text")
        # 清空内容
        self.msgList    = []

    def login(self):
        url = "https://www.p2peye.com/member.php?mod=login_ty"
        userNameLocator = (By.NAME, "username")
        pwdLocator = (By.NAME, "password")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(userNameLocator))
        except TimeoutException:
            raise Exception, u"Error:登录界面定位失败！"
        else:
            self.driver.find_element(*userNameLocator).send_keys(self.user)
            self.driver.find_element(*pwdLocator).send_keys(self.pwd)
            self.driver.find_element_by_id("login-ty-sub").click()

    def getReward(self):
        url = "https://licai.p2peye.com/club"
        signBtnLocator = (By.ID, "signBtn")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(signBtnLocator))
        except TimeoutException:
            # import pdb;pdb.set_trace()
            self.sendMsg(u"Error:签到按钮定位失败！")
        else:
            self.driver.find_element(*signBtnLocator).click()
            self.sendMsg(u"P2P天眼签到成功！")
        self.driver.save_screenshot("xx.png") # 这也是把整个页面截取下来了
        self.sendMsg(os.path.join(PATH,"xx.png"), "image")

def start():
    for account in ACCOUNTS:
        user        = account["user"]
        pwd         = account["pwd"]
        msgManger   = MsgManager()
        driver      = initialDriver(msgManger)
        p2peyeInstance = p2peye(driver, user, pwd, msgManger)
        driverList.append(driver)
        try:
            loginStatus = p2peyeInstance.login()
            p2peyeInstance.getReward()
        except:
            # import pdb;pdb.set_trace()
            import traceback
            msgManger.sendMsg(traceback.format_exc(), "text")

def quit():
    global driverList
    for driver in driverList:
        driver.quit()
    del driverList[:]

def getTimeDelta():
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=11, minute=40)
    delta = tom1 - now
    return delta.total_seconds()

def main():
    start()
    timedelta = getTimeDelta()
    threading.Timer(timedelta, main).start()
    quit()

if __name__ == '__main__':
    main()