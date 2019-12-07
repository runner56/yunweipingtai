#-*- coding:utf8 -*-

import os, sys, time, threading, random, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image


sys.path.append("..")
from conf import JXY_Conf 
from emailapi import emailApi
from qywx import MsgManager

PATH = os.getcwd() # 当前目录，用于存储验证码图片
ACCOUNTS = JXY_Conf["ACCOUNTS"]
TIMER = JXY_Conf["TIMER"]
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

class jxy:
    def __init__(self, driver, user, pwd, msgManger):
        self.driver        = driver
        self.user          = user
        self.pwd           = pwd
        self.msgManger     = msgManger
        self.uCoin         = ""
        self.keys          = []
        self.hoes          = []
        self.msgList       = []
        self.emailApi      = emailApi()
        self.redirectTimes = 5  # 加入重置次数限制，避免循环


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
        self.msgList.insert(0, u"账号：%s" % self.user)
        self.msgList.append(self.uCoin)
        self.msgList.append(u"钥匙: %s" % ",".join(self.keys))
        self.msgList.append(u"锄头: %s" % ",".join(self.hoes))
        # msg = "\r\n".join(self.msgList)
        msg = "\r\n".join([unicode(i) for i in self.msgList]) # 解决msgList出现None的问题
        self.msgManger.sendMsg(msg, "text")

        # 清空内容
        self.uCoin      = ""
        self.keys       = []
        self.hoes       = []
        self.msgList    = []

    def getYZM(self):
        # x = emailApi()
        while True:
            time.sleep(8)
            yzm = self.msgManger.getYZM()
            if yzm in [None,""]:
                yzm = self.emailApi.recvEmail()
            if yzm:
                print yzm
                break
        self.sendMsg(u"输入的验证码: %s" % yzm)
        return yzm

    def requestUrl(self, url):
        self.driver.get(url)
        if self.driver.current_url!=url and self.driver.current_url.find("login")!=-1:
            self.sendMsg(u"ERROR：登录过期，需重新登录！\nurl:%s\ncurrent_url:%s" % (url, self.driver.current_url))
            self.redirectTimes -= 1
            if self.redirectTimes > 0:
                self.login()
                return True
            else:
                sys.exit()

        self.redirectTimes = 5  # 重置次数
        return False

    # 定时器
    def processJXYTimer(self):
        self.appendMsgList(u"启动定时器")
        try:
            self.digMine()
            self.forgeMineral()
            self.processTreasure()
        except Exception,e:
            import traceback
            msg = traceback.format_exc().decode("utf8")
            self.sendMsg(u"账号%s出现异常%s" % (self.user,msg))

        try:
            self.driver.current_window_handle
        except:
            self.sendMsg(u"无法定位到driver的handle，退出定时器！")
        else:
            timer = threading.Timer(TIMER, self.processJXYTimer)
            timer.start()
        finally:
            self.appendMsgList(u"定时器结束")
            self.sendMsgList() # 把储存的列表信息整理发出去

    # 登录
    def login(self):
        url = "http://www.juxiangyou.com/login/index"
        self.requestUrl(url)
        yzmLocator = (By.CSS_SELECTOR, "img.J_validate_code")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(yzmLocator))
        except TimeoutException:
            self.sendMsg(u"加载登录界面失败")
            return self.login()
        else:
            yzmElement = self.driver.find_element_by_class_name("J_validate_code")
            
            self.driver.save_screenshot("xx.png") # 这也是把整个页面截取下来了

            left = int(yzmElement.location["x"])
            top = int(yzmElement.location["y"])
            right = int(yzmElement.location["x"]+yzmElement.size["width"])
            bottom = int(yzmElement.location["y"]+yzmElement.size["height"])

            im = Image.open("xx.png")
            im = im.crop((left, top, right, bottom))
            im.save("yzm.png")

            self.driver.find_element_by_id("account").send_keys(self.user)
            self.driver.find_element_by_id("password").send_keys(self.pwd)
            
            self.sendMsg(os.path.join(PATH,"yzm.png"), "image")
            self.sendMsg(u"输入验证码,格式:@+验证码")
            
            yzm = self.getYZM() # 循环阻塞
            
            
            self.driver.find_element_by_id("code").send_keys(yzm)

            # self.driver.find_element_by_class_name("J_userlogin").click() # 点击登录
            self.driver.execute_script("document.getElementsByClassName('J_userlogin')[0].click()") # 通过js点击登录
            userLinkLocator = (By.CSS_SELECTOR, "a.user-link")
            try:
                WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(userLinkLocator))
                self.sendMsg(u"%s登录成功！" % self.user)
                self.sign()
                self.buyMineral() # 18.5.23不需要购买矿石了，亏本；18.12.26加入矿石购买
                return "LoginSuccess"
            except TimeoutException:
                self.sendMsg(u"%s登录失败！" % self.user)
                return self.login()

            

    # 签到
    def sign(self):
        url = "http://www.juxiangyou.com/sign"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        signBtnLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.sign-btn.J_sign")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(signBtnLocator))
        except TimeoutException:
            self.appendMsgList(u"已完成签到，不必再签！")
        else:
            signBtn = self.driver.find_element_by_css_selector("i.icon.btn-sprite.sign-btn.J_sign")
            signBtn.click()
            self.appendMsgList(u"签到成功！")
            time.sleep(2)
            confirmSignBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
            confirmSignBtn.click()
            time.sleep(2)

        # 判断是否达到累积签到
        reachBtns = self.driver.find_elements_by_xpath("//ul[@class='four-squares']/li/i")
        if len(reachBtns)==0:
            self.appendMsgList(u"累积签到定位有误")
        for i,reachBtn in enumerate(reachBtns):
            if reachBtn.get_attribute("class")=="icon btn-sprite get-btn J_getPrize": #not-reached-btn, get-btn, got-btn
                self.appendMsgList(u"累积签到%d天，领取奖励" %(i*5+5))
                reachBtn.click()
                time.sleep(2)
                break


    def getUcoinNum(self):
        """当前U币的数量"""
        locator = (By.CSS_SELECTOR, "div.user-ubi")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            self.appendMsgList(u"ERROR:无法定位到U币框！")
            return
        return self.driver.find_element_by_css_selector("div.user-ubi").text


    # 挖矿
    def digMine(self):
        
        url = "http://www.juxiangyou.com/forge/mineral"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        # 收矿
        gainMineralBtnLocator = (By.CSS_SELECTOR, "div.btn_win")
        closeMsgLocator = (By.XPATH, "//div[@class='common-fuceng-box']//div[@class='awardText']")
        closeBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_closeCommonFc")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(gainMineralBtnLocator))
        except TimeoutException:
            self.appendMsgList(u"无矿石可以收获")
        else:
            gainMineralBtn = self.driver.find_element(*gainMineralBtnLocator)
            gainMineralBtn.click()
            
            try:
                WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(closeBtnLocator))
                # WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(closeMsgLocator))
            except TimeoutException:
                self.appendMsgList(u"ERROR:定位关闭按键失败！")
            else:
                closeMsg = u",".join([i.text for i in self.driver.find_elements(*closeMsgLocator)])
                self.appendMsgList(u"收获矿石%s" % closeMsg)
                self.driver.find_element(*closeBtnLocator).click()
        try: # 通过锄头动画来判断是否在挖矿
            self.driver.find_element_by_css_selector("div.bar_runing")
            countDown = self.driver.find_element_by_css_selector("div.countDown").text
            self.appendMsgList(u"正在挖矿，剩余时间%s" % countDown)
        except NoSuchElementException:
            # 选锄
            flag = False # 判断是否有锄头的标识
            hoes = self.driver.find_elements_by_xpath("//div[@class='mineral-column']//li") # 6个锄头
            for hoe in reversed(hoes):
                if hoe.text.find(u"未拥有")>-1:
                    continue
                flag = True
                self.appendMsgList(u"使用锄头%s挖矿" % hoe.text.split("\n")[0])
                hoe.click()
                time.sleep(2)
                break
            if flag == False:
                if self.buyTool():
                    self.digMine()
                return
            else:
                # 选矿
                mineralHoleBtn = self.driver.find_element_by_css_selector("div.mine.mine"+str(random.randint(1,3)))
                mineralHoleBtn.click()
                time.sleep(2)
                # 开始挖矿
                btnOk = self.driver.find_element_by_xpath("//div[@class='mineral-column']//div[@class='btn ok']")
                btnOk.click()
                time.sleep(2)

        # 挖矿后获取锄头的数量
        for i in self.driver.find_elements_by_xpath("//span[@class='columns-yellow']"):
            self.hoes.append(i.text)
        

    # 购买锄头
    def buyTool(self):
        url = "http://www.juxiangyou.com/forge/shop?type=tool"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return False
        buyBtnLocator = (By.XPATH, "//ul[@class='stones tools J_buyTools']/li[3]/i[@class='icon btn-sprite buy']")
        confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_buyToolConfirm")
        closeBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_closeCommonFc")
        closeMsgLocator = (By.XPATH, "//div[@class='common-fuceng-box']//div[@class='text']")
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(buyBtnLocator))
        except TimeoutException:
            self.appendMsgList(u"ERROR:无法定位到购买按键！")
            return False
        buyBtn = self.driver.find_element(*buyBtnLocator)
        buyBtn.click()
        
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(confirmBtnLocator))
        except TimeoutException:
            self.appendMsgList(u"ERROR:无法定位到确认按键！")
            return False
        confirmBtn = self.driver.find_element(*confirmBtnLocator)
        confirmBtn.click()

        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(closeBtnLocator))
        except TimeoutException:
            self.appendMsgList(u"ERROR:无法定位到关闭按键！")
            return False
        closeMsg = self.driver.find_element(*closeMsgLocator).text.strip()
        closeBtn = self.driver.find_element(*closeBtnLocator)
        closeBtn.click()
        self.appendMsgList(closeMsg)
        if closeMsg == u"U币不足，购买失败！":
            return False
        return True #u"U币不足，购买失败！":

    # 购买矿石
    def buyMineral(self):
        url = "http://www.juxiangyou.com/forge/shop?type=ore"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return False
        locator = (By.XPATH, "/html/body/div[3]/div[5]/div[2]/div[6]/span") # 通过出现"锻造商城"来判断页面加载完成
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except:
            self.appendMsgList(u"ERROR:加载商店页面失败！")
            return False

        # self.appendMsgList(u"完成商店页面加载")

        mineralLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.buy")
        confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_buyStoneConfirm")
        closeBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_closeCommonFc")
        closeMsgLocator = (By.XPATH, "//div[@class='common-fuceng-box']//div[@class='text']")

        while True:
            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(mineralLocator))
            except TimeoutException:
                self.appendMsgList(u"矿石已售完")
                break
            mineralElement = self.driver.find_element(*mineralLocator)
            mineralElement.click()

            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(confirmBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"未弹出购买矿石确认框")
                break
            confirmBuyBtn = self.driver.find_element(*confirmBtnLocator) # 确认购买
            confirmBuyBtn.click()

            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(closeBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"未弹出购买矿石的结果提示框！")
                break
            closeBtn = self.driver.find_element(*closeBtnLocator) # 购买结果提示框
            closeMsg = self.driver.find_element(*closeMsgLocator).text.strip()
            closeBtn.click()
            self.appendMsgList(closeMsg)
            if closeMsg == u"U币不足，购买失败！":
                break
            
    # 锻造钥匙
    def forgeMineral(self):
        url = "http://www.juxiangyou.com/forge/hall"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        hallBottomLocator = (By.CLASS_NAME, "hall-bottom") # 底部的锻造格子来判断是否完成加载
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(hallBottomLocator))
        except:
            self.appendMsgList(u"加载矿石商店失败，退出购买")
            return
        
        takeOutKeyBtnLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.take-out.J_takeOut")
        # 取出锻造好的钥匙
        while True:
            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(takeOutKeyBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"无钥匙可取")
                break #跳出循环
            else:
                finishedKey = self.driver.find_element_by_css_selector("i.icon.btn-sprite.take-out.J_takeOut")
                finishedKey.click()
                time.sleep(2)
                confirmTakeBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
                confirmTakeBtn.click()
                self.appendMsgList(u"取出钥匙")
                time.sleep(2)


        # 往空的锻造框锻造钥匙
        startForgeBtnLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.forge-it.J_startForge")
        while True:
            try:
                WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(startForgeBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"无空格可以锻造")
                break
            else:
                self.driver.find_element(*startForgeBtnLocator).click()
                time.sleep(2)
                selectForgeBtns = self.driver.find_elements_by_css_selector("i.icon.little-btns.forge-it.J_forge")
                if len(selectForgeBtns)>0:
                    selectForgeBtns[-1].click()
                    self.appendMsgList(u"锻造钥匙")
                    time.sleep(2)
                    confirmForgeBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_sureForgeBtn")
                    confirmForgeBtn.click() # 注意，点击完确定后会刷新网页
                    time.sleep(10) # 点击完确定后会刷新网页，等待10s等它页面刷新完成
                else:
                    self.appendMsgList(u"矿石不足")
                    break
          
    # 合成宝箱
    def processTreasure(self):
        url = "http://www.juxiangyou.com/forge/treasure"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return 
        # 如何在加载完成前就执行
        takeOutBtnLocator = (By.CSS_SELECTOR, "a.key-btn.take-out")
        composeBtnLocator = (By.CSS_SELECTOR, "a.key-btn.compose")
        while True:
            try:
                WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(takeOutBtnLocator))
            except TimeoutException:
                self.appendMsgList(u"无可取出的钥匙")
                break
            else:
                takeOutBtn = self.driver.find_element_by_css_selector("a.key-btn.take-out")
                takeOutBtn.click()
                self.appendMsgList(u"取出钥匙")
                time.sleep(2)
                confirmBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
                confirmBtn.click()

        # 在取出钥匙后，存储钥匙数量
        for i in self.driver.find_elements_by_xpath("//span[@class='key-count']/i[@class='count']"):
            self.keys.append(i.text)

        while True:
            try:
                composeBtn = self.driver.find_element_by_xpath("//a[@class='key-btn compose'][not(@enabled)]")
            except NoSuchElementException:
                self.appendMsgList(u"无可合成的钥匙")
                break
            else:
                composeBtn.click()
                self.appendMsgList(u"合成钥匙")
                sureBtnLocator    = (By.CSS_SELECTOR, "i.little-btns.confirm.J_surecompose")
                confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.ok.J_closeCommonFc")
                try:
                    WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(sureBtnLocator))
                except TimeoutException:
                    self.appendMsgList(u"未弹出合成提示框！")
                else:
                    sureBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_surecompose")
                    sureBtn.click()
                try:
                    WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(confirmBtnLocator))
                except TimeoutException:
                    self.appendMsgList(u"未弹出合成确认框！")
                else:
                    confirmBtn = self.driver.find_element_by_css_selector("i.little-btns.ok.J_closeCommonFc")
                    confirmBtn.click()

        self.uCoin = self.getUcoinNum()   # 在合成宝箱之后获取当前的U币数量

def start():
    global driverList
    for account in ACCOUNTS:
        user        = account["user"]
        pwd         = account["pwd"]
        msgManger   = MsgManager()
        driver      = initialDriver(msgManger)
        jxyInstance = jxy(driver, user, pwd, msgManger)
        driverList.append(driver)
        loginStatus = jxyInstance.login()
        if loginStatus == "LoginSuccess":
            jxyInstance.processJXYTimer()

def restart():
    global driverList
    for driver in driverList:
        driver.quit()
    del driverList[:]
    main()

def getTimeDelta():
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=7, minute=30)
    delta = tom1 - now
    return delta.total_seconds()

def main():
    start()
    timedelta = getTimeDelta()
    threading.Timer(timedelta, restart).start()

if __name__ == '__main__':
    main()

