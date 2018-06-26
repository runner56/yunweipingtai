# -*- coding:utf-8 -*-
import redis

class redisComponent(object):
    def __init__(self):
        super(redisComponent, self).__init__()
        self.r = redis.Redis(host='localhost',port=6379,db=0)

    def save(self, key, value):
        self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)