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


class P2Peye(object):
    __path    = os.getcwd() # 当前目录，用于存储验证码图片
    __acounts = P2PEYE_Conf["ACCOUNTS"]

    def __init__(self, driver, msgManger):
        self.driver    = driver
        self.msgManger = msgManger

    def run(self):
        for account in self.__acounts:
            user        = account["user"]
            pwd         = account["pwd"]
            try:
                self.__login(user, pwd)
                self.__sign()
            except:
                import traceback
                self.msgManger.sendMsg(traceback.format_exc().decode("utf8"), "text")
                # 必须进行utf8解码，要不然注释的中文是utf8编码的。在后面用replace会出现编码错误。
            self.__flushcookie()

    def __login(self, user, pwd):
        url = "https://www.p2peye.com/member.php?mod=login_ty"
        userNameLocator = (By.NAME, "username")
        pwdLocator = (By.NAME, "password")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(userNameLocator))
        except TimeoutException:
            raise Exception, u"P2Peye Error:登录界面定位失败！"
        else:
            self.driver.find_element(*userNameLocator).send_keys(user)
            self.driver.find_element(*pwdLocator).send_keys(pwd)
            # self.driver.find_element_by_id("login-ty-sub").click() # POST登录，后续还得再判断登录是否成功，无法点击，被图片挡住了
            self.driver.execute_script("document.getElementById('login-ty-sub').click()") # 改为使用js模拟点击
        
        promptLocator = (By.ID, "myprompt")
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(promptLocator))
        except TimeoutException:
            raise Exception, u"P2Peye Error:登录无响应！"

    def __sign(self):
        url = "https://licai.p2peye.com/club"
        signBtnLocator = (By.ID, "signBtn")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(signBtnLocator))
        except TimeoutException:
            self.msgManger.sendMsg(u"P2Peye Error:签到按钮定位失败！", "text")
        else:
            # self.driver.find_element(*signBtnLocator).click() # 无法点击，被图片挡住了
            self.driver.execute_script("document.getElementById('signBtn').click()") # 使用js来模拟点击
            self.msgManger.sendMsg(u"P2P天眼签到成功！", "text")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(1000,0)") # 滚动到最右端，方便截图
        self.driver.save_screenshot("p2peye.png") # 这也是把整个页面截取下来了
        self.msgManger.sendMsg(os.path.join(self.__path,"p2peye.png"), "image")

    def __flushcookie(self):
        self.driver.delete_all_cookies()
