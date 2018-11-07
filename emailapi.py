# -*- coding:utf8 -*-

import poplib, email, datetime, time
from conf import EMAIL_OPTIONS

OPTIONS = EMAIL_OPTIONS
class emailApi(object):
    def __init__(self):
        self.host = OPTIONS.get("HOST")
        self.port = OPTIONS.get("PORT")
        self.user = OPTIONS.get("USER")
        self.pass_ = OPTIONS.get("PASS")
        self.lastTimeStamp = None
        self.connection = self.openPopConnection()

    def openPopConnection(self):
        connection = None
        try:
            connection = poplib.POP3_SSL(self.host, self.port)
            connection.user(self.user)
            connection.pass_(self.pass_)

        except Exception,e:
            import traceback
            print u"连接失败！"
            print traceback.format_exc().decode("utf8")
            return None

        print u"邮箱登录成功！"
        return connection

    def parseMailSubject(self, msg):
        subStr = msg.get("subject")
        if subStr:
            subList = email.Header.decode_header(subStr)
            subinfo = subList[0][0]
            if subinfo[0] == "@":   # 以@开头的才是验证码
                return subinfo[1:]
        return None

    def recvEmail(self):
        try:
            self.connection = self.openPopConnection()
            mailCount, size = self.connection.stat()
            message = self.connection.retr(mailCount)[1]
            mail = email.message_from_string('\n'.join(message))
            utcstr = mail.get("date")
            d = datetime.datetime.strptime(utcstr, "%a, %d %b %Y %H:%M:%S +0800")
            t = d.timetuple()
            ts = int(time.mktime(t))
            ts = float(str(ts)+str("%06d" % d.microsecond))/1000000
            if ts==self.lastTimeStamp:
                print self.lastTimeStamp
                return None
            self.lastTimeStamp = ts
            return self.parseMailSubject(mail)
        except: # 重新登录
            self.connection = self.openPopConnection()


if __name__ == '__main__':
    x = emailApi()
    x.recvEmail()