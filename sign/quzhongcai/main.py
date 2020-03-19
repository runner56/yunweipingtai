import requests, urllib, json, logging
import time

logger = logging.getLogger(__name__)

class qzc(object):
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

    proxies = {"http": "http://127.0.0.1:9999","https": "https://127.0.0.1:9999"}

    get_g_token_url = "https://newidea4-gamecenter-backend.1sapp.com/x/user/token"  # 获取g_token
    get_ticket_url = "https://newidea4-gamecenter-backend.1sapp.com/x/open/game"    # 打开游戏获取ticket
    get_s_token_url = "https://game-center-tree-game.1sapp.com/x/tree-game/user"    # 获取s_token
    coin_balance_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/coin-balance" # 当前金币
    add_plant_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/add-plant" # 种菜
    plant_ok_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/plant-ok"  # 收菜
    remove_bug_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/remove-bug"  # 除虫
    get_pool_info_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/pool/info"   # 获取水池状态
    with_water_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/pool/with-draw"  # 打水
    water_plants_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/water-plants" # 浇水
    plant_info_url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/info"    # 获取植物状态

    def __init__(self, token):
        self.token = token
        self.g_token = None
        self.s_token = None
        self.plants_info = None
        self.drips = 0
        self.coins = 0

    @classmethod
    def _decode_payload(self, payload):
        """#payload中有%3D，requests会对%强制做urlencode，所以先使用urllib来对payload做unquote"""
        t = urllib.request.unquote(json.dumps(payload))
        return json.loads(t)

    def get_g_token(self):
        """
        获取g_token：{"code":0,"message":"成功","showErr":0,"currentTime":1581131457,"data":{"g_token":"2eBNL6pJrGKi-7OMr7A8-eqJnj15WZ-4u6NqAGCi-7Oi979i-vTUDsBfL6nRAGCJrj9fWG1g-GtkrvYl9vp497yl-8-393Kf-GTir6piW6KJcp==","mid":""}}
        """
        payload = self._decode_payload({
            "token": self.token,
            "app_id": "a3MptZsE5qE5",   # 不能少，少了无法定位到用户
            "platform": "gapp"
        })
        # res = requests.get(self.get_g_token_url).json()
        res = requests.get(self.get_g_token_url, params=payload).json()
        logger.debug(res)
        self.g_token = res["data"]["g_token"]

    def get_ticket(self):
        """
        获取ticket：{"code":0,"message":"成功","showErr":0,"currentTime":1581142210,"data":{"url":"https://newidea4-gamecenter-frontend.1sapp.com/game/prod/farm_shell/index.html?app_id=a3MptZsE5qE5\u0026app_name=%E8%B6%A3%E7%A7%8D%E8%8F%9C%E5%8F%91%E8%A1%8CAPP\u0026appid=a3MptZsE5qE5\u0026dc=\u0026dtu=\u0026ext=eyJzb3VyY2UiOiIifQ%3D%3D\u0026origin_type=0\u0026platform=gapp\u0026sdk_version=cocos.2ec6fcdb0d9ef5ac289e.js\u0026sign=f788491e7edf8f817abe5ae2902fd425\u0026tag_id=\u0026ticket=t11XfTMwBaQ3nwd7UjsNw\u0026time=1581142210\u0026uuid=","name":"趣种菜发行app","icon":"http://newidea4-gamecenter-cms.1sapp.com/icons/20191210/11XZdxaVVVeGq4rHexPZ.png","screen_location":2,"qruntime":"{\"enable\":false,\"hot_start\":false,\"unify_load\":false,\"menu\":false}","countdown":{"is_exist":false,"duration":0,"reward_coin":0,"status":0}}}
        """
        payload = self._decode_payload({
            "app_id": "a3MptZsE5qE5",
            "platform": "gapp",
            "g_token": self.g_token
        })
        res = requests.get(self.get_ticket_url, params=payload).json()
        logger.debug(res)
        url = res["data"]["url"]
        self.ticket = url.split("ticket=")[1].split("&")[0]

    def get_s_token(self):
        """
        获取s_token：{"code":0,"message":"成功","showErr":0,"currentTime":1581131495,"data":{"s_token":"2eBfL6pJrG9N-vTq9GAbAo_Va6yfnjx5msAF97TM97Kf97pk-PqJm81oaJAFAGAeWGAq-7meWjKk9G9fWvuU93pU98xG-fpk-7KMu6KMAo4=","nickname":"用户946667357","avatar":"https://static-oss.qutoutiao.net/jpg/touxiang.jpg","open_id":"u11XbjiZ1h4YFBaBGg2Fh"}}
        """
        payload = self._decode_payload({
            "ticket": self.ticket, # 不可删除
        })
        res = requests.get(self.get_s_token_url, params=payload, headers=self.urlencode_headers).json()
        logger.debug(res)
        self.s_token = res["data"]["s_token"]

    def init_game(self):
        self.get_g_token()
        self.get_ticket()
        self.get_s_token()

    def get_coin_balance(self):
        """{"code":0,"message":"成功","showErr":0,"currentTime":1578844930,"data":{"num":795}}"""
        payload = self._decode_payload({
            "s_token": self.s_token, # 不可移除
        #     "token": "90008nv0Ho8bPoBwuFVWMEf6NB8i6syC4dhf9nSQCK9Z3qaY0KLpyITkb-H9a89ExPQB2DICjFrIOSjQzWvc6TxoouIjC9F1sSvhpdL8jmM", # 可移除
        #     "platform": "gapp",
        #     "g_token": "2eBNL6pJrGKi-7OMr7A8-eqJnj15WZ-4u6NqAGCi-7mMrvpf-fAqDsBfL6nRAGCJrj-lu7Ai-GAk9fygu3W3-ftUuG_g98Tf9Gl19jKk-7uJcp%3D%3D", # 可移除 可移除
        #     "source": "287001",
        #     "app_id": "a3MptZsE5qE5",
        #     "origin_type": "0",
        #     "device_code": "867469026039387",
        #     "dtu": "10661",
        #     "vn": "1.1.7.000.0110.1811",
        #     "tk": "ACEneZ-hCcAdq7wGtr0uC8qFciXbqkGUF_BnbXF6Yw",
        #     "v": "10107000",
        #     "dc": "867469026039387",
        #     "tuid": "J3mfoQnAHau8Bra9LgvKhQ",
        #     "user_mode": ""
        })
        res = requests.get(self.coin_balance_url, params=payload, headers=self.urlencode_headers).json()
        logger.debug(res)
        if res.get("code")!=0:
            logger.critical("获取金币出错！")
            return False
        self.coins = res["data"]["num"]
        return True

    def add_plant(self, plant_id):
        """
        1是番茄，5是茄子，3是西瓜
        {
            "code": 0,
            "message": "成功",
            "showErr": 0,
            "currentTime": 1578844599,
            "data": {
                "plant_info": {
                    "plant_id": 3,
                    "status": 2,
                    "absorb_waters": 0,
                    "left_time": 14400,
                    "level": 1,
                    "level_value": 500,
                    "drips_value": 10,
                    "is_affect": 0
                },
                "my_box": null
            }
        }
        """
        files = {
            "plant_id": (None, plant_id),
            "s_token": (None, self.s_token)
        }
        res = requests.post(self.add_plant_url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res.get("code")!=0:
            logger.critical("种植物出错！")
            return False
        logger.info("种植物成功")
        return True

    def plant_ok(self):
        """{"code":0,"message":"成功","showErr":0,"currentTime":1578844028,"data":{"coin_num":500,"drips_num":10,"level_extra_num":0,"envelope_money":1698,"envelope_addition":8}}"""
        files = {
            "s_token": (None, self.s_token)
        }
        res = requests.post(self.plant_ok_url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res.get("code")!=0:
            logger.critical("收植物出错！")
            return False
        logger.info("成功收取植物，获得%d金币，%d水滴", res["data"]["coin_num"], res["data"]["drips_num"])
        return True

    def remove_bug(self):
        """返回数据：{"code":0,"message":"成功","showErr":0,"currentTime":1578844016,"data":{"left_time":-1578844016}}"""
        files = {
            "s_token": (None, self.s_token)
        }
        res = requests.post(self.remove_bug_url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res.get("code")!=0:
            logger.critical("除虫出错！")
            return False
        return True

    def water_plants(self):
        """
        {
            "code": 0,
            "message": "成功",
            "showErr": 0,
            "currentTime": 1578845225,
            "data": {
                "plant_info": {
                    "plant_id": 3,
                    "status": 2,
                    "absorb_waters": 100,
                    "left_time": 13774,
                    "level": 5,
                    "level_value": 615,
                    "drips_value": 14,
                    "is_affect": 0
                },
                "drips": 71
            }
        }
        """
        files = {
            "s_token": (None, self.s_token)
        }
        res = requests.post(self.water_plants_url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res.get("code")!=0:
            logger.critical("浇水出错！")
            return False
        self.drips = res["data"]["drips"]
        logger.info("浇水一次")
        return True

    def get_pool_info(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1581148442,"data":{"pool_drips":0,"capacity":120,"is_speed":false,"left_speed_up_time":0,"speed":20,"left_speed_times":6}}
        """
        payload = self._decode_payload({
            "s_token": self.s_token, # 不可删除
        })
        res = requests.get(self.get_pool_info_url, params=payload, headers=self.urlencode_headers).json()
        logger.debug(res)

    def pool_speed_up(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1581224270,"data":{"left_speed_up_time":14400,"left_speed_times":5,"speed":40}}
        可加速六次，每次持续4小时
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/pool/speed-up"
        files = {
            "s_token": (None, self.s_token)
        }
        res = requests.post(url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        logger.info("水池加速产水，输出信息：%s" % res["data"])
        return True


    def with_water(self):
        """{"code":0,"message":"成功","showErr":0,"currentTime":1578843815,"data":{"drips_num":120}}"""
        files = {
            "s_token": (None, self.s_token)
        }
        res = requests.post(self.with_water_url, files=files, headers=self.file_request_headers).json()
        logger.debug(res)
        if res.get("code"):
            logger.warning("收水滴失败！")
            return False
        self.drips += res["data"]["drips_num"]
        logger.info("收到%d水滴，目前总共有%d水滴", res["data"]["drips_num"], self.drips)
        return True

    def get_plant_info(self):
        """
        返回数据
        {
            "code": 0,
            "message": "成功",
            "showErr": 0,
            "currentTime": 1579326233,
            "data": {
                "drips": 0,
                "plants_info": [{   # 如果未种植物，为空列表
                    "plant_id": 3,
                    "status": 2,
                    "absorb_waters": 290,
                    "left_time": 12240,
                    "level": 9,
                    "level_value": 888,
                    "drips_value": 20,
                    "is_affect": 0
                }],
                "plants_v2": {...可查看日志查看详情，太多了},
                "is_new_user": 0,
                "new_user_coin": 1400,
                "new_user_plant": [1, 2],
                "plant_ok_num": 7,
                "is_white_user": false,
                "first_login": false,
                "my_box": {
                    "status": 1,
                    "red_heart": 15,
                    "switch": 1
                },
                "rabbit": {
                    "left_time": 0
                },
                "sign_over": 0,
                "level": {
                    "daily_reward": 0
                },
                "carrot": {
                    "left_time": 0
                },
                "first_login_time": 1577836714,
                "ab": {
                    "new_user": 2
                },
                "red_envelope": {
                    "money": 1858
                },
                "new_user_step": 3
            }
        }
        """
        self.get_coin_balance()
        payload = self._decode_payload({
            "s_token": self.s_token, # 不可移除
        })
        res = requests.get(self.plant_info_url, params=payload, headers=self.urlencode_headers).json()
        logger.debug(res)

        msg = ""
        if res.get("code"):
            logger.error("获取状态信息出错！")
            return False
        data = res["data"]
        self.drips = data["drips"]
        msg += "目前有%d金币与%d水滴" % (self.coins, self.drips)
        if data.get("red_envelope"):
            money = data["red_envelope"]["money"]
            msg += "，红包金额为%0.2f元" % (money/100)

        if len(data["plants_info"]) == 0:
            msg += "，土地为空，可以种植物！"
            logger.info(msg)
            return True

        self.plants_info = data["plants_info"][0]
        plants_v2 = data["plants_v2"]
        plant_id = self.plants_info["plant_id"]
        left_time = self.plants_info["left_time"]
        plant_name = plants_v2[str(plant_id)]["name"]
        level = self.plants_info["level"]
        level_value = self.plants_info["level_value"]

        if left_time > 0:
            msg += "，植物<%s>%d秒后可收获，目前等级%d，可收获金币%d" % (plant_name, left_time, level, level_value)
        else:
            msg += "，植物<%s>已成熟，目前等级%d，可收获金币%d" % (plant_name, level, level_value)

        logger.info(msg)
        return True

    def get_catch_doll_info(self):
        """
        获取抓娃娃信息：{"code":0,"message":"成功","showErr":0,"currentTime":1579328387,"data":{"left_times":10,"left_video_times":1}}
        """
        url = "http://game-center-self-middle.1sapp.com/x/middle/catch-doll/info"
        params = self._decode_payload({
            "s_token": self.s_token,
        })
        res = requests.get(url, params=params).json()
        logger.debug(res)
        if res["data"]["left_video_times"] == 0:
            return False
        return True

    def catch_doll_watch_video(self):
        """
        看视频获取次数：{"code":0,"message":"成功","showErr":0,"currentTime":1579350280,"data":{"left_times":5,"left_video_times":0}}
        """

        url = "http://game-center-self-middle.1sapp.com/x/middle/catch-doll/video"
        files = {
            "s_token": (None, self.s_token),
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        return True

    def catch_doll(self):
        """
        抓娃娃：{"code":0,"message":"成功","showErr":0,"currentTime":1579328429,"data":{"pool_id":3,"reward_config":{"reward_id":2,"weight":1000,"objects":[{"object_id":9,"object_num":66}]},"left_times":9,"envelope_flag":true}}
        没有抓到：{'code': 0, 'message': '成功', 'showErr': 0, 'currentTime': 1581167131, 'data': {'pool_id': 3, 'reward_config': {'reward_id': 0, 'weight': 10000, 'objects': []}, 'left_times': 6, 'envelope_flag': False}}
        """
        url = "http://game-center-self-middle.1sapp.com/x/middle/catch-doll/do"
        files = {
            "s_token": (None, self.s_token),
            "pool_id": (None, 3)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)

        if res["code"]:
            logger.warning(res["message"])
            return False

        if res["data"]["envelope_flag"]:
            self.catch_doll_take_reward()
            logger.info("抓娃娃获取%d金币，还剩%d次", res["data"]["reward_config"]["objects"][0]["object_num"], res["data"]["left_times"])
        else:
            logger.info("抓娃娃未获取到奖励，还剩%d次", res["data"]["left_times"])
        if res["data"]["left_times"]:
            return True
        return False

    def catch_doll_take_reward(self):
        """
        获取奖励：{"code":0,"message":"成功","showErr":0,"currentTime":1579328556,"data":{"objects":[{"object_id":9,"object_num":66}]}}
        没有奖励：{'code': 20011, 'message': '您当前没有奖励哦', 'showErr': 0, 'currentTime': 1581167131, 'data': {}}
        """
        url = "http://game-center-self-middle.1sapp.com/x/middle/catch-doll/take-reward"
        files = {
            "s_token": (None, self.s_token),
            "pool_id": (None, 3)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)

    def click_plant(self):
        """
        每小时可以点击一次植物，得60金币
        {"code":0,"message":"成功","showErr":0,"currentTime":1579329172,"data":{"coin_num":60,"left_time":3600}}
        {"code":1006,"message":"现在还不能点萝卜哦","showErr":0,"currentTime":1579329250,"data":{}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/activity/carrot/take-reward"
        files = {
            "s_token": (None, self.s_token),
            "extra": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return
        logger.info("点击植物获得%d金币", res["data"]["coin_num"])

    def get_sign_info(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579348059,"data":{"sign_record":[1,1,1,1,1,1,1],"reward":[60,10,20,50,10,20,120],"today":18}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/activity/sign/info"
        params = self._decode_payload({
            "s_token": self.s_token,
        })
        res = requests.get(url, params=params).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])
        return res["data"]["sign_record"]

    def sign(self, day):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579347792,"data":{"coin_value":60}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/activity/sign/do"
        files = {
            "s_token": (None, self.s_token),
            "extra": (None, 1),
            "day": (None, day)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return
        logger.info("第%d天签到成功，获得%d金币", day, res["data"]["coin_value"])

    def box_rand(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579348229,"data":{"prize_id":4,"my_gift_box_info":{"status":1,"red_heart":10,"switch":1}}}
        {"code":3005,"message":"爱心数量不足，还不能抽奖哦","showErr":0,"currentTime":1579348541,"data":{}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/box/my/rand-reward"
        files = {
            "s_token": (None, self.s_token),
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        logger.info("抽盒子，还剩%d爱心", res["data"]["my_gift_box_info"]["red_heart"])
        self.box_take_reward()
        return True

    def box_take_reward(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579348357,"data":{"coin_num":0,"drips_num":20}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/box/my/take-reward"
        files = {
            "s_token": (None, self.s_token),
            "extra": (None,1)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return
        logger.info("抽盒子获得%d金币, %d水滴", res["data"]["coin_num"], res["data"]["drips_num"])

    def catch_rabbit(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579329470,"data":{"bingo":0}}
        {"code":87,"message":"抓兔子还在倒计时中哦","showErr":0,"currentTime":1579329658,"data":{}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/activity/rabbit/catch"
        files = {
            "s_token": (None, self.s_token),
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        if res["data"]["bingo"]:
            self.catch_rabbit_take_reward()
        else:
            logger.info("抓兔子，未获得奖励")
        return True

    def catch_rabbit_take_reward(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579329608,"data":{"coin_value":60,"left_time":3600}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/activity/rabbit/take-reward"
        files = {
            "s_token": (None, self.s_token),
            "extra": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return
        logger.info("抓兔子，获得奖励%d金币", res["data"]["coin_value"])

    def get_flop_info(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579350550,"data":{"physical":5,"left_time":50,"left_video_times":1}}
        """
        url = "http://game-center-tree-game.1sapp.com/x/middle/flop/info"
        params = self._decode_payload({
            "s_token": self.s_token,
        })
        res = requests.get(url, params=params).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("进入翻牌界面："+res["message"])
            return False
        logger.info("进入翻牌界面")
        return True

    def start_flop(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1579350589,"data":{"normal":[9,8],"addition":[5],"reward_pool":{"1":{"reward_id":1,"object":{"...
        {"code":1011,"message":"体力不足","showErr":0,"currentTime":1579352314,"data":{}}
        """
        url = "http://game-center-tree-game.1sapp.com/x/middle/flop/start"
        params = self._decode_payload({
            "s_token": self.s_token,
        })
        res = requests.get(url, params=params).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("开始翻牌："+res["message"])
            return False
        logger.info("开始翻牌")
        self.flop_video()
        self.flop_take_reward()
        return True

    def flop_video(self):
        """
        翻牌，得两次翻牌机会{"code":0,"message":"成功","showErr":0,"currentTime":1579350943,"data":{"type":1}}
        """
        url = "http://game-center-tree-game.1sapp.com/x/middle/flop/video"
        files = {
            "s_token": (None, self.s_token),
            "type": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("翻牌：看视频"+res["message"])
            return
        logger.info("翻牌：看视频获得两次翻牌机会")

    def flop_take_reward(self):
        """
        {"code":1009,"message":"您当前没有获得奖励哦","showErr":0,"currentTime":1579352315,"data":{}}
        {"code":0,"message":"成功","showErr":0,"currentTime":1579351013,"data":{"reward":{"9":65}}}
        """
        url = "http://game-center-tree-game.1sapp.com/x/middle/flop/take-reward"
        files = {
            "s_token": (None, self.s_token),
            "extra": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("翻牌：获取奖励"+res["message"])
            return
        logger.info("翻牌：获取奖励%s", res["data"])

    def flop_video_2(self):
        """
        翻牌，看视频得游戏次数
        {"code":0,"message":"成功","showErr":0,"currentTime":1579352627,"data":{"type":2,"physical":3,"left_time":1573}}
        {'code': 0, 'message': '成功', 'showErr 0, 'currentTime': 1581220080, 'data': {'type': 0}}
        """
        url = "http://game-center-tree-game.1sapp.com/x/middle/flop/video"
        files = {
            "s_token": (None, self.s_token),
            "type": (None, 2)
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning("看视频获取游戏次数："+res["message"])
            return False
        if res["data"]["type"] == 0:
            logger.warning("翻牌，看视频未获得体力")
            return False
        logger.info("翻牌，看视频获得体力%s", res["data"]["physical"])
        return True

    # 偷菜
    def steal_plant(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1581220583,"data":{"coin_num":12,"gift_box":true,"water":false,"steal":false,"type":"steal","turntable_left_times":3}}
        {'code': 0, 'message': '成功', 'showErr': 0, 'currentTime': 1581221491, 'data': {'coin_num': 0, 'gift_box': True, 'water': False, 'steal': False, 'type': '', 'turntable_left_times': 3}}
        """
        url = "https://game-center-tree-game.1sapp.com/x/tree-game/gapp/social/behave-in-friends"
        files = {
            "s_token": (None, self.s_token),
            "type": (None, "steal")
        }
        res = requests.post(url, files=files).json()
        logger.debug(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        logger.info("偷菜，得金币%s", res["data"]["coin_num"])
        return True

    def get_clock_12_activity_info(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1581220741,"data":{"start_time":1581220800,"end_time":1581222600,"button_id":"1","menu_id":"1","extra_param":["450","3","8"],"day_coin":0,"all_coin":0,"pools":[{"pool_id":1,"play_time":0,"can_play_time":1}]}}
        """
        url = "https://game-center-self-middle.1sapp.com/x/middle/award-pool/get-info"
        files = {
            "s_token": (None, self.s_token),
            "config_type": (None, 3)
        }
        res = requests.post(url, files=files).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        logger.info("12点活动，返回信息%s", res["data"])
        return True

    def get_clock_12_activity_take_reward(self):
        url = "http://game-center-chicken.1sapp.com/x/middle/award-pool/take-award"
        files = {
            "s_token": (None, self.s_token),
            "config_type": (None, 3),
            "pool_id": (None, 1),
            "extra": (None, 1) # 待核实
        }
        res = requests.post(url, files=files).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])
            return

        logger.info("12点活动，获奖信息%s", res["data"])

    def get_clock_19_activity_info(self):
        """
        {"code":0,"message":"成功","showErr":0,"currentTime":1581246027,"data":{"start_time":1581246000,"end_time":1581251400,"button_id":"1","menu_id":"1","extra_param":[],"day_coin":60,"all_coin":60,"pools":[{"pool_id":1,"play_time":1,"can_play_time":1},{"pool_id":2,"play_time":0,"can_play_time":1}]}}
        """
        url = "https://game-center-self-middle.1sapp.com/x/middle/award-pool/get-info"
        files = {
            "s_token": (None, self.s_token),
            "config_type": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])
            return False
        logger.info("19点活动，返回信息%s", res["data"])
        return True

    def get_clock_19_activity_take_reward(self):
        """
        第一次获取
        {"code":0,"message":"成功","showErr":0,"currentTime":1581246019,"data":{"play_time":1,"day_coin":60,"all_coin":60,"objects":[{"object_id":9,"object_num":60,"object_name":""}]}}
        第二次获取
        {"code":0,"message":"成功","showErr":0,"currentTime":1581246123,"data":{"play_time":1,"day_coin":260,"all_coin":260,"objects":[{"object_id":9,"object_num":200,"object_name":""}]}}
        """
        url = "http://game-center-chicken.1sapp.com/x/middle/award-pool/take-award"
        files = {
            "s_token": (None, self.s_token),
            "config_type": (None, 1),
            "pool_id": (None, 1)
        }
        res = requests.post(url, files=files).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])

        files = {
            "s_token": (None, self.s_token),
            "config_type": (None, 1),
            "pool_id": (None, 2)
        }
        res = requests.post(url, files=files).json()
        logger.info(res)
        if res["code"]:
            logger.warning(res["message"])
            return

        logger.info("19点活动，获奖信息%s", res["data"])


class qzc_strategy(qzc):

    def __init__(self, token):
        super(qzc_strategy, self).__init__(token)

    def run(self):
        self.init_game()

        self.pool_speed_up_strategy()

        self.click_plant()

        self.catch_doll_strategy()

        self.box_strategy()

        self.catch_rabbit_strategy()

        self.flop_strategy()

        self.steal_plant_strategy()

        self.get_clock_12_activity_take_reward()

        self.get_clock_19_activity_take_reward()

        

        if self.get_plant_info() is False:
            return False

        if self.plants_info is None:
            self.add_plant(3)
            self.get_plant_info()
        time.sleep(1)

        self.get_pool_info()
        # time.sleep(1)
        self.with_water()

        if self.plants_info["is_affect"]:
            self.remove_bug()

        time.sleep(1)

        max_drips_times = 25 - self.plants_info["drips_value"]
        while self.drips >= 10 and max_drips_times > 0: # 西瓜25次浇水即可
            self.water_plants()
            max_drips_times -= 1
            time.sleep(0.5)

        if self.plants_info["left_time"] < 0:
            self.plant_ok()
            self.add_plant(3)
        self.get_plant_info()



        # sign_record = self.get_sign_info()
        # for i in range(1,8):
        #     self.sign(i)
        # 签到这个考虑移除，签到活动

    def catch_doll_strategy(self):
        """一天抓一次娃娃"""
        f1 = True
        f2 = True
        while f1:
            while f2:
                f2 = self.catch_doll()
                time.sleep(2)
            f1 = self.catch_doll_watch_video()
            f2 = True

    def box_strategy(self):
        flag = True
        while flag:
            flag = self.box_rand()

    def catch_rabbit_strategy(self):
        flag = True
        while flag:
            flag = self.catch_rabbit()

    def flop_strategy(self):
        self.get_flop_info() # 需先进入界面才会刷新次数
        f1 = True
        f2 = True
        while f1:
            while f2:
                f2 = self.start_flop()
                time.sleep(2)
            f1 = self.flop_video_2()
            f2 = True

    def steal_plant_strategy(self):
        flag = True
        while flag:
            flag = self.steal_plant()
            time.sleep(1)

    def pool_speed_up_strategy(self):
        flag = True
        while flag:
            flag = self.pool_speed_up()
            time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, format = "%(levelname)-8s %(asctime)s %(name)s %(message)s")
    logger = logging.getLogger(__name__)
    token = "fb50SPzU8WxtlIg_P2fZJf0mU8ehcd9PgFpE7NmYRHQ1QRgrP1zXfetRzoQ1n3qcpUAvJU93vyOSJrb0fiNgLdMVhXw0OLgjRHHQGTjDwVg"
    a = qzc_strategy(token)
    a.run()

