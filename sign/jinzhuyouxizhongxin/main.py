import requests, urllib, json, logging
import time

logger = logging.getLogger(__name__)

class JinZhuYouXiZhongXin(object):
    urlencode_headers = {
        "Host": "game-center-tree-game.1sapp.com" ,
        "Connection": "keep-alive" ,
        "Accept": "application/json, text/plain, */*" ,
        "Origin": "https://newidea4-gamecenter-frontend.1sapp.com" ,
        "x-wap-profile": "http://wap1.huawei.com/uaprof/HONOR_Che2-UL00_UAProfile.xml" ,
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; Che2-UL00 Build/HonorChe2-UL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 qapp_android qapp_version_10107000" ,
        "Accept-Encoding": "gzip, deflate" ,
        "Accept-Language": "zh-CN,en-US;q=0.8" ,
        "X-Requested-With": "com.heitu.qzc"
    }

    file_request_headers = {
        "Host": "game-center-tree-game.1sapp.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://newidea4-gamecenter-frontend.1sapp.com",
        "x-wap-profile": "http://wap1.huawei.com/uaprof/HONOR_Che2-UL00_UAProfile.xml",
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; Che2-UL00 Build/HonorChe2-UL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 qapp_android qapp_version_10107000",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,en-US;q=0.8",
        "X-Requested-With": "com.heitu.qzc"
    }

    def __init__(self, token, tk):
        self.token = token
        self.g_token = None
        self.tk = tk

    @classmethod
    def _decode_payload(self, payload):
        """#payload中有%3D，requests会对%强制做urlencode，所以先使用urllib来对payload做unquote"""
        t = urllib.request.unquote(json.dumps(payload))
        return json.loads(t)

    def get_g_token(self):
        """
        获取g_token
        {"code":0,"message":"成功","showErr":0,"currentTime":1581571491,"data":{"g_token":"2eBNL6pJrGKe9f9e-vmkrsqJnj15WZ-4u6NqAGCi-7Oi-7mi-vgiDsBfL6nRAGCJu8A4u7AU-7BJ-fnl-vAeWj949f-gu8pq-GTkWGTqr7TJcp==","mid":""}}
        """
        url = "https://game-center-new.1sapp.com/x/user/token"
        payload = self._decode_payload({
            "token": self.token,
            "app_id": "a3DAGqSqpLSC",   # 不能少，少了无法定位到用户
            "platform": "gcu",
            "tk": self.tk,  # 不能少
        })
        res = requests.get(url, params=payload).json()
        logger.debug(res)
        if res["code"]:
            logger.error("获取g_token失败："+res["message"])
            return
        self.g_token = res["data"]["g_token"]


    def heartBeat(self):
        """
        发送第一个心跳包: {"code":0,"message":"","data":{"result":true}}
        """
        url = "https://game-center-member.1sapp.com/x/v1/goldpig/heartbeat"
        files = {
            "token": (None, self.token),
            "g_token": (None, self.g_token)
        }
        res = requests.post(url, files = files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("金猪，发送心跳1："+res["message"])
            return
        logger.info("金猪，发送心跳1，成功！")
        time.sleep(3)

        """
        发送第二个心跳包: {"code":0,"message":"","data":{"result":true}}
        """
        timestamp = int(time.time()*1000)
        url = "https://game-center-member.1sapp.com/x/v1/goldpig/heartbeat?request_timestamp=%d" % timestamp
        files = {
            "g_token": (None, self.g_token),
            "session_timestamp": (None, timestamp-3)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("金猪，发送心跳2：" + res["message"])
            return
        logger.info("金猪，发送心跳2，成功！")

    def withDraw(self):
        """
        {"code":0,"message":"","data":{"coin":20,"remainCoin":0,"ad":false}}

        """
        url = "http://game-center-member.1sapp.com/x/v1/goldpig/withdraw?request_timestamp=%d" % int(time.time()*1000)
        files = {
            "g_token": (None, self.g_token),
            "isDouble": (None, True)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("点击金猪：" + res["message"])
            return
        logger.info("点击金猪，获得%d金币", res["data"]["coin"])

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, format = "%(levelname)-8s %(asctime)s %(name)s %(message)s")
    logger = logging.getLogger(__name__)
    token = "0262ANREf7z4rqrYnw5uxfTPin_rtn2ef3Uwaps5Tzx-LYeaO6Dhq1UbPJGI8JXoAq1lKEp2L3PTZXVr1hhOKfDgxxht3oN7o9S4S1w"
    tk = "ACEneZ-hCcAdq7wGtr0uC8qFroU9SCBfc_BnbXF0dA"
    a = qzc_strategy(token)
    a.run()
