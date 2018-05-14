# -*- coding:utf-8 -*-

import sys, os

# sys.path.append("./api/src/") # 主程序(yunweipingtai)已加了环境路径，不用再添加
from CorpApi import *
from conf import *


weWorkApi = CorpApi(Conf["CORP_ID"], Conf["APP_SECRET"])
