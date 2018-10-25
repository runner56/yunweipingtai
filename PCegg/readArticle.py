#-*- coding:utf8 -*-

import requests, time, json, sys

sys.path.append("..")
from conf import PCEGGS_ACCOUNTS

# 每天最多获取49500币
# 单篇文章最多50次奖励，25000币

class readArticle(object):
	__getArticleListUrl = "http://games.q9x9.com/app_information_flow/article/queryArticleList" #userId=27332503&pageNo=1

	__openArticleUrl = "http://games.q9x9.com/app_information_flow/article/queryShareMsg" #userId=27332503&articleId=1275

	__getGoldMoneyUrl = "http://games.q9x9.com/app_information_flow/article/addUserArticleGoldMoney" #userId=27332503&articleId=1275&type=2

	def __init__(self):
		self.stroageDict = {}

	def getArticleList(self, userId):
		while True:
			try:
				rsp = requests.get(self.__getArticleListUrl, params={"userId":userId,"pageNo":"1"})
				print "%s %s" % (userId, u"获取文章列表")
				break
			except requests.exceptions.ConnectionError:
				time.sleep(3)
				continue
		ct = json.loads(rsp.content, encoding="utf-8")
		self.stroageDict.setdefault(userId, {})["content"] = ct
		self.stroageDict.setdefault(userId, {})["index"] = 0
		self.stroageDict.setdefault(userId, {})["articleGolds"] = 0
		self.stroageDict.setdefault(userId, {})["totalGolds"] = 0

	def getGoldMoney(self, userId, articleId, t):
		rsp = requests.get(self.__getGoldMoneyUrl, params={"userId":userId, "articleId":articleId, "type":t})
		ct = json.loads(rsp.content, encoding="utf-8")
		if ct.get("status") == 0:
			self.stroageDict[userId]["articleGolds"] += 500
			self.stroageDict[userId]["totalGolds"] += 500
		else:
			self.getArticle(userId)
		print u"%s，文章%s %d，总获取%d，%s" % (
				userId,
				articleId,
				self.stroageDict[userId]["articleGolds"],
				self.stroageDict[userId]["totalGolds"],
				rsp.content.decode("utf8"))

	def getArticle(self, userId):
		datas = self.stroageDict.get(userId).get("content").get("datas")
		i = self.stroageDict.get(userId).get("index",0)
		if i < len(datas):
			article = datas[i]
			self.stroageDict.setdefault(userId, {})["articleGolds"] = 0
			self.stroageDict.setdefault(userId, {})["articleId"] = article.get("id")
			self.stroageDict.setdefault(userId, {})["articleType"] = article.get("articleType")
			self.stroageDict.setdefault(userId, {})["index"] = i + 1
		else:
			self.getArticleList(userId)
			self.getArticle(userId)
			

	def run(self):
		for account in PCEGGS_ACCOUNTS:	#获取文章列表
			time.sleep(1)
			userid = account.get("userid")
			self.getArticleList(userid)
			self.getArticle(userid)
		while True:
			for userid,v in self.stroageDict.items():
				time.sleep(1)
				try:
					self.getGoldMoney(userid, v["articleId"], v["articleType"])
				except requests.exceptions.ConnectionError:
					print u"%s 请求失败！" % userid
			time.sleep(30)

if __name__ == '__main__':
	i = readArticle()
	i.run()
