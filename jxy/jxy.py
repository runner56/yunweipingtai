#-*- coding:utf8 -*-

import os, sys, time, threading, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image

from qywx import MsgManager

PATH = os.getcwd() # 当前目录
ACCOUNTS = (
    {
        "user":"bupt_devilman@126.com",
        "pwd":"bbguy1989"
    },{
        "user":"759775069@qq.com",
        "pwd":"bbguy1989"
    }
)

# 初始化
def initialDriver(msgManger):
    msgManger.processMsg(u"初始化浏览器！")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--proxy-server=socks5://localhost:7001")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

class jxy:
    def __init__(self, driver, user, pwd, msgManger):
        self.driver    = driver
        self.user      = user
        self.pwd       = pwd
        self.msgManger = msgManger
        self.uCoin     = ""
        self.keys      = []
        self.hoes      = []
        self.msgList   = []
    
    def clearContent(self): # 待完善
        self.uCoin     = ""
        self.keys      = []
        self.hoes      = []
        self.msgList   = []

    def requestUrl(self, url):
        self.driver.get(url)
        if self.driver.current_url != url:
            self.login()
            return True
        return False
        # time.sleep(2)

    # 定时器
    def processJXYTimer(self):
        self.msgManger.processMsg(u"启动定时器")
        self.digMine()
        self.forgeMineral()
        self.processTreasure()
        timer = threading.Timer(1200, self.processJXYTimer)
        timer.start()
        self.msgManger.processMsg(u"定时器结束")
        self.clearContent() # 待完善
        self.msgManger.sendTextMsg()

    # 登录
    def login(self):
        url = "http://www.juxiangyou.com/login/index"
        self.requestUrl(url)
        yzmLocator = (By.CSS_SELECTOR, "img.J_validate_code")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(yzmLocator))
        except TimeoutException:
            self.msgManger.directTransMsg(u"加载登录界面失败")
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
            
            self.msgManger.processMsg(os.path.join(PATH,"yzm.png"), "image")
            self.msgManger.directTransMsg(u"输入验证码,格式:@+验证码")

            while True:
                time.sleep(8)
                yzmCode = self.msgManger.getYZM()
                if yzmCode:
                    self.msgManger.directTransMsg(u"输入的验证码: %s" % yzmCode)
                    break
            
            # yzmCode = raw_input(u"请输入验证码：".encode("gbk"))
            self.driver.find_element_by_id("code").send_keys(yzmCode)

            self.driver.find_element_by_class_name("J_userlogin").click() # 点击登录
            userLinkLocator = (By.CSS_SELECTOR, "a.user-link")
            try:
                WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(userLinkLocator))
                self.msgManger.directTransMsg(u"登录成功！")
                self.sign()
                self.buyMineral()
                return "LoginSuccess"
            except TimeoutException:
                self.msgManger.directTransMsg(u"登录失败！")
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
            self.msgManger.processMsg(u"已完成签到，不必再签！")
        else:
            signBtn = self.driver.find_element_by_css_selector("i.icon.btn-sprite.sign-btn.J_sign")
            signBtn.click()
            self.msgManger.processMsg(u"签到成功！")
            time.sleep(2)
            confirmSignBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
            confirmSignBtn.click()
            time.sleep(2)

        # 判断是否达到累积签到
        reachBtns = self.driver.find_elements_by_xpath("//ul[@class='four-squares']/li/i")
        if len(reachBtns)==0:
            self.msgManger.processMsg(u"累积签到定位有误")
        for i,reachBtn in enumerate(reachBtns):
            if reachBtn.get_attribute("class")=="icon btn-sprite get-btn J_getPrize": #not-reached-btn, get-btn, got-btn
                self.msgManger.processMsg(u"累积签到%d天，领取奖励" %(i*5+5))
                reachBtn.click()
                time.sleep(2)
                break

    # 挖矿
    def digMine(self):
        
        url = "http://www.juxiangyou.com/forge/mineral"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        # 收矿
        gainMineralBtnLocator = (By.CSS_SELECTOR, "div.btn_win")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(gainMineralBtnLocator))
        except TimeoutException:
            self.msgManger.processMsg(u"无矿石可以收获")
        else:
            gainMineralBtn = self.driver.find_element_by_css_selector("div.btn_win")
            gainMineralBtn.click()
            self.msgManger.processMsg(u"收获矿石成功")
            time.sleep(2)
            confirmSignBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
            confirmSignBtn.click()
        try: # 通过锄头动画来判断是否在挖矿
            self.driver.find_element_by_css_selector("div.bar_runing")
            # self.msgManger.processMsg(u"正在挖矿")
        except NoSuchElementException:
            # 选锄
            flag = False # 判断是否有锄头的标识
            hoes = self.driver.find_elements_by_xpath("//div[@class='mineral-column']//li") # 6个锄头
            for hoe in reversed(hoes):
                if hoe.text.find(u"未拥有")>-1:
                    continue
                flag = True
                self.msgManger.processMsg(u"使用锄头%s挖矿" % hoe.text.split("\n")[0])
                hoe.click()
                time.sleep(2)
                break
            if flag == False:
                self.buyTool()
                self.digMine() # 如何避免死循环？
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
        
        self.msgManger.hoes = self.hoes

    # 购买锄头
    def buyTool(self):
        url = "http://www.juxiangyou.com/forge/shop?type=tool"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        buyBtnLocator = (By.XPATH, "//ul[@class='stones tools J_buyTools']/li[3]/i[@class='icon btn-sprite buy']")
        confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_buyToolConfirm")
        closeBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_closeCommonFc")
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(buyBtnLocator))
        except TimeoutException:
            self.msgManger.processMsg(u"ERROR:无法定位到购买按键！")
            return
        buyBtn = driver.find_element_by_xpath("//ul[@class='stones tools J_buyTools']/li[3]/i[@class='icon btn-sprite buy']")
        buyBtn.click()
        
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(confirmBtnLocator))
        except TimeoutException:
            self.msgManger.processMsg(u"ERROR:无法定位到确认按键！")
            return
        confirmBtn = driver.find_element_by_css_selector("i.little-btns.confirm.J_buyToolConfirm")
        confirmBtn.click()

        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(closeBtnLocator))
        except TimeoutException:
            self.msgManger.processMsg(u"ERROR:无法定位到关闭按键！")
            return
        closeBtn = driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
        closeBtn.click()
        self.msgManger.processMsg(u"成功购买一个鹤嘴锄")

    # 购买矿石
    def buyMineral(self):
        url = "http://www.juxiangyou.com/forge/shop?type=ore"
        isRedirect = self.requestUrl(url)
        if isRedirect:
            return
        locator = (By.XPATH, "/html/body/div[3]/div[5]/div[2]/div[6]/span") # 通过出现"锻造商城"来判断页面加载完成
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except:
            self.msgManger.processMsg(u"ERROR:加载商店页面失败！")
            return

        # self.msgManger.processMsg(u"完成商店页面加载")

        mineralLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.buy")
        confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_buyStoneConfirm")
        successBuyLocator = (By.CSS_SELECTOR, "i.little-btns.confirm.J_closeCommonFc")

        while True:
            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(mineralLocator))
                mineralElement = self.driver.find_element_by_css_selector("i.icon.btn-sprite.buy")
                mineralElement.click()
            except TimeoutException:
                self.msgManger.processMsg(u"矿石已售完")
                break

            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(confirmBtnLocator))
                confirmBuyBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_buyStoneConfirm") # 确认购买
                confirmBuyBtn.click()
            except TimeoutException:
                self.msgManger.processMsg(u"未弹出购买矿石确认框")
                break

            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(successBuyLocator))
                successBuyBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc") # 购买成功
                successBuyBtn.click()
            except TimeoutException:
                self.msgManger.processMsg(u"未弹出成功购买矿石的提示框！")
                break

            self.msgManger.processMsg(u"成功购买矿石")

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
            self.msgManger.processMsg(u"加载矿石商店失败，退出购买")
            return
        
        takeOutKeyBtnLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.take-out.J_takeOut")
        # 取出锻造好的钥匙
        while True:
            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(takeOutKeyBtnLocator))
            except TimeoutException:
                self.msgManger.processMsg(u"无钥匙可取")
                break #跳出循环
            else:
                finishedKey = self.driver.find_element_by_css_selector("i.icon.btn-sprite.take-out.J_takeOut")
                finishedKey.click()
                time.sleep(2)
                confirmTakeBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
                confirmTakeBtn.click()
                self.msgManger.processMsg(u"取出钥匙")
                time.sleep(2)


        # 往空的锻造框锻造钥匙
        startForgeBtnLocator = (By.CSS_SELECTOR, "i.icon.btn-sprite.forge-it.J_startForge")
        while True:
            try:
                WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(startForgeBtnLocator))
            except TimeoutException:
                self.msgManger.processMsg(u"无空格可以锻造")
                break
            else:
                emptyGrid = self.driver.find_element_by_css_selector("i.icon.btn-sprite.forge-it.J_startForge")
                emptyGrid.click() # 不可点击？？？？
                time.sleep(2)
                selectForgeBtns = self.driver.find_elements_by_css_selector("i.icon.little-btns.forge-it.J_forge")
                if len(selectForgeBtns)>0:
                    selectForgeBtns[-1].click()
                    self.msgManger.processMsg(u"锻造钥匙")
                    time.sleep(2)
                    confirmForgeBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_sureForgeBtn")
                    confirmForgeBtn.click() # 注意，点击完确定后会刷新网页
                    time.sleep(10) # 点击完确定后会刷新网页，等待10s等它页面刷新完成
                else:
                    self.msgManger.processMsg(u"矿石不足")
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
                self.msgManger.processMsg(u"无可取出的钥匙")
                break
            else:
                takeOutBtn = self.driver.find_element_by_css_selector("a.key-btn.take-out")
                takeOutBtn.click()
                self.msgManger.processMsg(u"取出钥匙")
                time.sleep(2)
                confirmBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_closeCommonFc")
                confirmBtn.click()

        # 在取出钥匙后，存储钥匙数量
        for i in self.driver.find_elements_by_xpath("//span[@class='key-count']/i[@class='count']"):
            self.keys.append(i.text)

        self.msgManger.keys = self.keys            

        while True:
            try:
                composeBtn = self.driver.find_element_by_xpath("//a[@class='key-btn compose'][not(@enabled)]")
            except NoSuchElementException:
                self.msgManger.processMsg(u"无可合成的钥匙")
                break
            else:
                composeBtn.click()
                self.msgManger.processMsg(u"合成钥匙")
                sureBtnLocator    = (By.CSS_SELECTOR, "i.little-btns.confirm.J_surecompose")
                confirmBtnLocator = (By.CSS_SELECTOR, "i.little-btns.ok.J_closeCommonFc")
                try:
                    WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(sureBtnLocator))
                except TimeoutException:
                    self.msgManger.processMsg(u"未弹出合成提示框！")
                else:
                    sureBtn = self.driver.find_element_by_css_selector("i.little-btns.confirm.J_surecompose")
                    sureBtn.click()
                try:
                    WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(confirmBtnLocator))
                except TimeoutException:
                    self.msgManger.processMsg(u"未弹出合成确认框！")
                else:
                    confirmBtn = self.driver.find_element_by_css_selector("i.little-btns.ok.J_closeCommonFc")
                    confirmBtn.click()

        self.uCoin = self.getUcoinNum()   # 在合成宝箱之后获取当前的U币数量
        self.msgManger.uCoin = self.uCoin

    def getUcoinNum(self):
        """当前U币的数量"""
        locator = (By.CSS_SELECTOR, "div.user-ubi")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            self.msgManger.processMsg(u"ERROR:无法定位到U币框！")
            return
        return self.driver.find_element_by_css_selector("div.user-ubi").text


if __name__ == '__main__':
    for account in ACCOUNTS:
        user        = account["user"]
        pwd         = account["pwd"]
        msgManger   = MsgManager(user)
        driver      = initialDriver(msgManger)
        jxyInstance = jxy(driver, user, pwd, msgManger)
        loginStatus = jxyInstance.login()
        if loginStatus == "LoginSuccess":
            jxyInstance.processJXYTimer()
