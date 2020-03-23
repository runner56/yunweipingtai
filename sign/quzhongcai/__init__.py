import sys, logging

sys.path.append("..")
from .main import *
from config import QZC_ACCOUNTS

logger = logging.getLogger(__name__)
logger.debug("成功导入pceggs模块")


def qzc():
    for account in QZC_ACCOUNTS:
        qzcThread(qzc_strategy(account["token"])).start()
