import sys

from .web import *
from .app import *

sys.path.append("..")
from config import PCEGGS_ACCOUNTS
import logging

logger = logging.getLogger(__name__)

logger.debug("成功导入pceggs模块")

def readNovel():
    for account in PCEGGS_ACCOUNTS:
        readNovelThread(app(**account)).start()

def readArticle():
    for account in PCEGGS_ACCOUNTS:
        readArticleThread(app(**account)).start()

def clockIn():
    for account in PCEGGS_ACCOUNTS:
        app(**account).clockIn()

def clockEnroll(paymoney=20):
    for account in PCEGGS_ACCOUNTS:
        app(**account).clockEnroll(paymoney)
