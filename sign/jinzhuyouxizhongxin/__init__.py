import threading, logging
import time

from main import *

class LoopTimer(threading.Thread):
    def __init__(self, GameInstance):
        threading.Thread.__init__(self)
        self.GameInstance = GameInstance
        t = int(time.time())
        self.mission = {
            "get_g_token":{
                "nts": t,
                "default": 3600*2
            },
            "heartBeat": {
                "nts": t+1,
                "default": 60
            },
            "withDraw": {
                "nts": t+2,
                "default": 600
            },
        }
        self.funcName = ""
        self.waitTime = 0
        self.finished = threading.Event()

    def updateMissionTime(self):
        self.mission[self.funcName]["nts"] = int(time.time()) + self.mission[self.funcName]["default"]
        logger.debug("updateMissionTime:" + str(self.mission))

    def getMissionTime(self):
        orderMissionList = sorted(self.mission.items(), key=lambda d:d[1]["nts"])
        logger.debug("getMissionTime:" + str(orderMissionList))
        self.funcName = orderMissionList[0][0]
        t1 = orderMissionList[0][1]["nts"]
        t2 = int(time.time())
        self.waitTime = 0 if t1<t2 else t1-t2

    def run(self):
        while True:
            self.getMissionTime()
            m, s = divmod(self.waitTime, 60)
            h, m = divmod(m, 60)
            logger.info("%02d:%02d:%02d后启动%s" , h, m, s, self.funcName)
            self.finished.wait(self.waitTime)  # wait信号阻塞，时间到后才往下执行
            if self.finished.is_set():
                self.finished.set()
                break
            func = getattr(self.GameInstance, self.funcName)
            func() # 不需要传递参数
            self.updateMissionTime()

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, format = "%(levelname)-8s %(asctime)s %(name)s %(message)s")
    logger = logging.getLogger(__name__)
    token = "0262ANREf7z4rqrYnw5uxfTPin_rtn2ef3Uwaps5Tzx-LYeaO6Dhq1UbPJGI8JXoAq1lKEp2L3PTZXVr1hhOKfDgxxht3oN7o9S4S1w"
    tk = "ACEneZ-hCcAdq7wGtr0uC8qFroU9SCBfc_BnbXF0dA"
    LoopTimer(JinZhuYouXiZhongXin(token, tk)).start()
