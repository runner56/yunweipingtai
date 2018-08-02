# -*- coding:utf8 -*-
import sys, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

sys.path.append("..")
if len(sys.argv)>1 and sys.argv[1]=="test":
    from qywx import TestMsgManager as MsgManager
else:
    from qywx import MsgManager

import pceggs

driver = None

def initialDriver(msgManager):
    timeStr = time.strftime("%H:%M:%S", time.localtime())
    msgManager.sendMsg(u"{} {}".format(timeStr, u"初始化浏览器！"), "text")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--proxy-server=socks5://localhost:7001")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def start():
    global driver
    msgManger = MsgManager()
    driver = initialDriver(msgManger)
    pceggsInstance = pceggs.PCeggs(driver, msgManger)
    pceggsInstance.run()

def quit():
    global driver
    driver.quit()

def getTimeDelta():
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=8, minute=30)
    delta = tom1 - now
    return delta.total_seconds()

def main():
    start()
    timedelta = getTimeDelta()
    threading.Timer(timedelta, main).start()
    quit()

if __name__ == '__main__':
    # main()
    start()