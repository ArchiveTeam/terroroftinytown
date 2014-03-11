# encoding=utf-8
import datetime
import tornado.gen
import tornado.ioloop


@tornado.gen.coroutine
def sleep(seconds):
    deadline = datetime.timedelta(seconds=seconds)
    yield tornado.gen.Task(
        tornado.ioloop.IOLoop.current().add_timeout, deadline
    )
