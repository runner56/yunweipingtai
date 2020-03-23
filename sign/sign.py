import sys, time, datetime, threading, argparse

class LoopTimer(threading.Thread):
    def __init__(self, function, args=[], kwargs={},  nt=(0,0), td=100):
        """
        nt相当于是定的某个时刻闹钟，如果是(0, 0)，就默认不启用闹钟模式，为选用时间间隔模式
        td就是时间间隔，如果nt不为(0,0)，则无意义
        """
        threading.Thread.__init__(self)
        self.nt = nt
        self.nthour = nt[0]
        self.ntmin = nt[1]
        self.td = td
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def _getTimeDelta(self):
        now = datetime.datetime.now()
        nt = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=self.nthour, minute=self.ntmin)
        delta = (nt - now).total_seconds()
        return delta if delta>=0 else delta+24*3600

    def run(self):
        while True:
            if self.nt == (0, 0):
                seconds = self.td
            else:
                seconds = self._getTimeDelta()
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            logger.info("%02d:%02d:%02d后启动%s" , h, m, s, self.function.__name__)
            self.finished.wait(seconds)  # wait信号阻塞，时间到后才往下执行
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args, **self.kwargs)

def main():
    LoopTimer(pceggs.clockIn, nt=(7,5)).start()
    LoopTimer(pceggs.readNovel, nt=(7,30)).start()
    LoopTimer(pceggs.readArticle, nt=(8,30)).start()
    LoopTimer(pceggs.clockEnroll, args=[20], nt=(23,55)).start()
    LoopTimer(quzhongcai.qzc, td=30*60).start()

if __name__ == '__main__':
    import logging
    sys.path.append("..")
    from config import init_log
    init_log()  # 初始化日志模块，只需初始化一次，放在其它库前面来初始化，怕其它库的日志污染
    logger = logging.getLogger()

    funcList = [
        'pceggs.clockIn',
        'pceggs.clockEnroll',
        'pceggs.readNovel',
        'pceggs.readArticle',
        'quzhongcai.qzc'
    ]

    helpStr = ""
    for i,j in enumerate(funcList):
        helpStr += "%2d--%s; " % (i, j)

    parser = argparse.ArgumentParser(description='网赚专用程序')
    parser.add_argument("-t", dest="test", action="store_true", help="启动测试，移除微信日志模块")
    parser.add_argument("-f", dest="StartImmediately", nargs="*", type=int, choices=range(5), default=[], help=helpStr)
    parser.add_argument("-s", dest="isStartTimer", action="store_false", help="不启动计时器")
    args = parser.parse_args()

    if args.test: # 测试状态则移除微信(HTTP)日志模块
        for handler in logger.handlers:
            if handler.name == "handler_wx":
                logger.removeHandler(handler)
        logger.debug("启动测试，移除微信日志模块！")

    for i in args.StartImmediately:
        module, func = funcList[i].split(".")
        func = getattr(__import__(module), func)
        func()

    import pceggs, p2peye, quzhongcai

    if args.isStartTimer:
        main()
