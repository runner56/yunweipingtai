#-*- coding:utf8 -*-

import sys
import xml.etree.cElementTree as ET
from requests import Request, Session
from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
from config import Flask_Conf

sys.path.append("./weworkapi/")
sys.path.append("./weworkapi/api/src/")
from weWorkMain import weWorkApi

sys.path.append("./valifyapi/")
from WXBizMsgCrypt import WXBizMsgCrypt

app = Flask(__name__)
api = Api(app)

sToken = Flask_Conf["sToken"]
sEncodingAESKey = Flask_Conf["sEncodingAESKey"]
sCorpID = Flask_Conf["sCorpID"]
ServerHost = Flask_Conf["ServerHost"]
ServerPort = Flask_Conf["ServerPort"]
FarmGameLog = Flask_Conf["FarmGameLog"]

YZM = ""

class receiveMsg(Resource):
    def get(self):
        """ 服务器验证 """
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        sVerifyMsgSig = request.args.get("msg_signature")
        sVerifyTimeStamp = request.args.get("timestamp")
        sVerifyNonce = request.args.get("nonce")
        sVerifyEchostr = request.args.get("echostr")        
        ret, sEchostr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchostr)
        if ret!=0:
            print u"ERR: VerifyURL ret: " + str(ret)
            return "ERROR"
        return int(sEchostr)    # 一定要转为int类型，不能加引号，否则验证失效

    def post(self):
        """ 接收与处理消息 """

        sReqMsgSig = request.args.get("msg_signature")
        sReqTimeStamp = request.args.get("timestamp")
        sReqNonce = request.args.get("nonce")
        sReqData = request.data # 可能错误
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if ret!=0:
            print "ERR:DecryptMsg ret: " + str(ret)
            return "ERROR"
        xml_tree = ET.fromstring(sMsg)
        msgType = xml_tree.find("MsgType").text
        if msgType=="text":
            content = xml_tree.find("Content").text # content是UNICODE的
            print content
            if content[0]=="@": #代表解析验证码
                global YZM
                YZM = content[1:]

        elif msgType=="event":
            event = xml_tree.find("Event").text
            eventKey = xml_tree.find("EventKey").text
            if eventKey=="farmgame":
                farmgameMsg()

        return "" # 空包返回，告知已经收到消息

class sendMsg(Resource):
    def get(self):
        msgType = request.args.get("type")
        if msgType not in ["text", "image"]:
            raise ValueError

        msg = request.args.get("msg")
        weWorkApi.sendMessage(msg, msgType)
        return "success"

    def post(self):
        """
        type:text/image
        msg: text类型时为文本，image类型时为文件路径
        """
        msgType = request.form.get("type")
        if msgType not in ["text", "image"]:
            raise ValueError
        msg = request.form.get("msg")
        weWorkApi.sendMessage(msg, msgType)

class getYZM(Resource):
    def get(self):
        global YZM
        yzm = YZM
        if yzm:
            YZM = ""
        return yzm

class setYZM(Resource):
    def get(self):
        global YZM
        yzm = request.args.get("yzm")
        YZM = yzm
        return "success"

@app.route("/farmgameMsg")
def farmgameMsg():
    with open(FarmGameLog, "rb") as f:
        t = f.readlines()[-6:]
    msg = "".join(t)
    weWorkApi.sendMessage(msg, "text")
    return "success"

@app.route("/farmgameMsg1")
def farmgameMsg1():
    farmgameMsg()
    # return redirect(url_for("farmgameMsg"))
    return "success1"

# 验证地址类似http://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323&echostr=ENCRYPT_STR
api.add_resource(receiveMsg, "/")
api.add_resource(sendMsg, "/sendMsg")
api.add_resource(getYZM, "/getYZM")
api.add_resource(setYZM, "/sendYZM")

if __name__ == "__main__":
    app.run(debug=True, host=ServerHost, port=ServerPort)