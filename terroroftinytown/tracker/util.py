# encoding=utf-8
import datetime
import tornado.gen
import tornado.ioloop


@tornado.gen.coroutine
def sleep(seconds):
    yield tornado.gen.sleep(seconds)
