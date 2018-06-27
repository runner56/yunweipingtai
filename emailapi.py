# -*- coding:utf8 -*-

<<<<<<< HEAD
import poplib, email, datetime, time
from conf import EMAIL_OPTIONS

=======
import poplib,email
from conf import EMAIL_OPTIONS


# def getYear(date):
#     rslt = re.search(r'\b2\d{3}\b', date)
#     return int(rslt.group())

# def getMonth(date):
#     monthMap = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
#                 'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12,}

#     rslt = re.findall(r'\b\w{3}\b', date)
#     for i in range(len(rslt)):
#         month = monthMap.get(rslt[i])
#         if None != month:
#             break

#     return month

# def getDay(date):
#     rslt = re.search(r'\b\d{1,2}\b', date)
#     return int(rslt.group())

# def getTime(date):
#     rslt = re.search(r'\b\d{2}:\d{2}:\d{2}\b', date)
#     timeList = rslt.group().split(':')

#     for i in range(len(timeList)):
#         timeList[i] = int(timeList[i])

#     return timeList

# def transformDate(date):
#     rslt = getYear(date)
#     rslt = rslt * 100
#     rslt = rslt + getMonth(date)
#     rslt = rslt * 100
#     rslt = rslt + getDay(date)
       

#     timeList = getTime(date)
#     for i in range(len(timeList)):
#         rslt = rslt * 100
#         rslt = rslt + timeList[i]

#     print(rslt)
#     return rslt

# def getRecentReadMailTime():
#     fp = open(CONFIG, 'r')
#     rrTime = fp.read()
#     fp.close()
#     return rrTime

# def setRecentReadMailTime():
#     fp = open(CONFIG, 'w')
#     fp.write(time.ctime())
#     fp.close()
#     return

# def parseMailSubject(msg):
#     subSrt = msg.get('subject')
#     if None == subSrt:
#         subject = '无主题'
#     else:
#         subList = header.decode_header(subSrt)
#         subinfo = subList[0][0]
#         subcode = subList[0][1]

#         if isinstance(subinfo,bytes):
#             subject = subinfo.decode(subcode)
#         else:
#             subject = subinfo

#     print(subject)
    
# def parseMailContent(msg):
#     if msg.is_multipart():
#         for part in msg.get_payload():
#             parseMailContent(part)
#     else:
#         bMsgStr = msg.get_payload(decode=True)
#         charset = msg.get_param('charset')
#         msgStr = 'Decode Failed'
#         try:
#             if None == charset:
#                 msgStr = bMsgStr.decode()
#             else:
#                 msgStr = bMsgStr.decode(charset)
#         except:
#             pass
        
#         print(msgStr)
        
# def recvEmail():
#     server = poplib.POP3(POP_ADDR)
#     server.user(USER)
#     server.pass_(PASS)

#     mailCount,size = server.stat()
#     mailNoList = list(range(mailCount))
#     mailNoList.reverse()

#     hisTime = transformDate(getRecentReadMailTime())
#     setRecentReadMailTime()
#     #pdb.set_trace()
#     for i in mailNoList:
#         message = server.retr(i+1)[1]
#         mail = email.message_from_bytes(b'\n'.join(message))

#         if transformDate(mail.get('Date')) > hisTime:
#             parseMailSubject(mail)
#             #parseMailContent(mail)
#         else:
#             break
        
# recvEmail()

# POP_ADDR = 'pop.qq.com'
# USER = ''
# PASS = ''
# CONFIG = ''
>>>>>>> c0e0589e302d4edf80b8e1480b3b89d10c6b2a3b
OPTIONS = EMAIL_OPTIONS

class emailApi(object):
    def __init__(self):
        self.host = OPTIONS.get("HOST")
        self.port = OPTIONS.get("PORT")
        self.user = OPTIONS.get("USER")
        self.pass_ = OPTIONS.get("PASS")
<<<<<<< HEAD
        self.lastTimeStamp = None
=======
>>>>>>> c0e0589e302d4edf80b8e1480b3b89d10c6b2a3b
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
            print traceback.format_exc()
            return None

        print u"登录成功！"
        return connection

    def parseMailSubject(self, msg):
        subStr = msg.get("subject")
        if subStr:
<<<<<<< HEAD
            subList = email.Header.decode_header(subStr)
=======
            subList = email.header.decode_header(subStr)
>>>>>>> c0e0589e302d4edf80b8e1480b3b89d10c6b2a3b
            subinfo = subList[0][0]
            if subinfo[0] == "@":   # 以@开头的才是验证码
                return subinfo[1:]
        return None

    def recvEmail(self):
<<<<<<< HEAD
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
=======
        mailCount, size = self.connection.stat()
        message = self.connection.retr(mailCount)[1]
        mail = email.message_from_string('\n'.join(message))
        self.parseMailSubject(mail)
>>>>>>> c0e0589e302d4edf80b8e1480b3b89d10c6b2a3b


if __name__ == '__main__':
    x = emailApi()
    x.recvEmail()