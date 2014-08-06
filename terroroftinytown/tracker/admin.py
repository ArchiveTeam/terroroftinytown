# encoding=utf-8
import tornado.web

from terroroftinytown.tracker.base import BaseHandler


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('admin/overview/index.html')

