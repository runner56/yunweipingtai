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
from conf import WW91_Conf 
from emailapi import emailApi
if sys.argv[1]=="test":
    from qywx import TestMsgManager as MsgManager
else:
    from qywx import MsgManager

# PATH = os.getcwd() # 当前目录，用于存储验证码图片
ACCOUNTS = WW91_Conf["ACCOUNTS"]
driverList = []

# 初始化
def initialDriver(msgManger):
    timeStr = time.strftime("%H:%M:%S", time.localtime())
    msgManger.sendMsg(u"{} {}".format(timeStr, u"初始化浏览器！"), "text")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--proxy-server=socks5://localhost:7001")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

class wenwen91(object):
    def __init__(self, driver, user, pwd, msgManger):
        self.driver    = driver
        self.user      = user
        self.pwd       = pwd
        self.msgManger = msgManger
        self.msgList   = []
        self.emailApi  = emailApi()

    def login(self):
        url = "https://www.91wenwen.net/user/login"
        self.driver.get(url)
        self.driver.find_element_by_id("login_account").send_keys(self.user)
        self.driver.find_element_by_id("login_password").send_keys(self.pwd)
        self.driver.find_element_by_class_name("login-btn").click()

    def vote(self):
        url = "https://www.91wenwen.net/vote/index"
        voteBtnLocator = (By.CSS_SELECTOR, "a.vote-btn.btn")
        selectRadioLocator = (By.ID, "answer_number_"+str(random.randint(1, 6)))
        while True:
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, 6, 0.5).until(EC.element_to_be_clickable(voteBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"已无投票")
                break
            else:
                self.driver.find_element(*voteBtnLocator).click()
                try:
                    WebDriverWait(self.driver, 6, 0.5).until(EC.element_to_be_selected)
                except TimeoutException:
                    self.appendMsgList(u"无法定位到选项，跳出循环")
                    break
                else:
                    self.driver.find_element(*selectRadioLocator).click()


def start():
    for account in ACCOUNTS:
        user        = account["user"]
        pwd         = account["pwd"]
        msgManger   = MsgManager()
        driver      = initialDriver(msgManger)
        ww91Instance = wenwen91(driver, user, pwd, msgManger)
        driverList.append(driver)
        ww91Instance.vote()
        loginStatus = ww91Instance.login()
        if loginStatus == "LoginSuccess":
            jxyInstance.sign()

def restart():
    global driverList
    for driver in driverList:
        driver.quit()
    del driverList[:]
    main()

def getTimeDelta():
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=7, minute=40)
    delta = tom1 - now
    return delta.total_seconds()

def main():
    start()
    timedelta = getTimeDelta()
    threading.Timer(timedelta, restart).start()

if __name__ == '__main__':
    main()