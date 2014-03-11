# encoding=utf-8
import tornado.web

from terroroftinytown.tracker.base import BaseHandler


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.redirect(self.reverse_url('admin.overview'))


class OverviewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('admin/overview.html')
