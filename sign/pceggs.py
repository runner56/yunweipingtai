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
from conf import PCEGGS_ACCOUNTS
from emailapi import emailApi

class PCeggs(object):
    __path = os.getcwd()

    def __init__(self, driver, msgManager):
        self.driver     = driver
        self.msgManager = msgManager

    def run(self):
        for account in PCEGGS_ACCOUNTS:
            user = account["user"]
            pwd = account["pwd"]
            try:
                self.__login(user, pwd)
                self.__sign()
            except:
                import traceback
                self.msgManger.sendMsg(traceback.format_exc().decode("utf8"), "text")
                # 必须进行utf8解码，要不然注释的中文是utf8编码的。在后面用replace会出现编码错误。
            self.__flushcookie()


    def __login(self, user, pwd):
        url = "http://www.pceggs.com/nologin.aspx"
        self.driver.get(url)
        loginBtnLocator = (By.ID, "Login_Submit")
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(loginBtnLocator))
        except TimeoutException:
            raise Exception, u"PCeggs:无法定位到登录按钮！"
        else:
            self.__input_login_info(user, pwd)

    def __input_login_info(self, user, pwd): # 输错验证码后可以再次输入，不必刷新页面
        loginMsgLocator = (By.ID, "div_msg")
        yzmElement      = self.driver.find_element_by_id("valiCode")
        yzmElement.click()
        self.__sendYZM(yzmElement)
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
            raise Exception, u"PCeggs:未定位到主页标识，可能已完成签到!"
        else:
            signDivLocator = (By.XPATH, "//div[contains(text(),'立即签到')]")
            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(signDivLocator))
                self.driver.find_element(*signDivLocator).click()
            except TimeoutException:
                raise Exception, u"PCeggs:签到失败，未定位到签到按钮!"
        finally:
            time.sleep(2)
            self.__screenshot()

    def __sendYZM(self, yzmElement):
        self.driver.save_screenshot("xx.png")
        left = int(yzmElement.location["x"])
        top = int(yzmElement.location["y"])
        right = int(yzmElement.location["x"]+yzmElement.size["width"])
        bottom = int(yzmElement.location["y"]+yzmElement.size["height"])
        im = Image.open("xx.png")
        im = im.crop((left, top, right, bottom))
        im.save("yzm.png")
        self.msgManager.sendMsg(os.path.join(self.__path, "yzm.png"), "image")
        self.msgManager.sendMsg(u"PCeggs:输入验证码,格式:@+验证码", "text")

    def __getYZM(self):
        while True:
            time.sleep(8)
            yzm = self.msgManager.getYZM()
            if yzm in [None,""]:
                yzm = emailApi.recvEmail()
            if yzm:
                print yzm
                break
        self.msgManager.sendMsg(u"PCeggs:输入的验证码: %s" % yzm, "text")
        return yzm

    def __screenshot(self):
        self.driver.execute_script("window.scrollTo(1000,0)")
        self.driver.save_screenshot("save_screenshot.png")
        self.msgManager.sendMsg(os.path.join(PATH, "save_screenshot.png"), "image")

    def __flushcookie(self):
        self.driver.delete_all_cookies()

