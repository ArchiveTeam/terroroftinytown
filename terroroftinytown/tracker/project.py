# encoding=utf-8
import tornado.web

from terroroftinytown.tracker.base import BaseHandler


class AllOverviewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        projects = self.application.db.all_projects()
        self.render('admin/all_projects.html', projects=projects)
