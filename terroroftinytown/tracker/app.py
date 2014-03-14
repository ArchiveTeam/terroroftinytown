# encoding=utf-8
import os.path
from tornado.web import URLSpec as U
import tornado.web

from terroroftinytown.tracker import account, admin, project
from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.ui import FormUIModule


class Application(tornado.web.Application):
    def __init__(self, database, **kwargs):
        self.db = database

        handlers = [
            U(r'/', IndexHandler),
            U(r'/admin/', admin.AdminHandler, name='admin'),
            U(r'/admin/login', account.LoginHandler, name='admin.login'),
            U(r'/admin/logout', account.LogoutHandler, name='admin.logout'),
            U(r'/users/', account.AllOverviewHandler, name='users.overview'),
            U(r'/user/([a-z0-9_-]*)', account.UserHandler, name='user.overview'),
            U(r'/admin/overview', admin.OverviewHandler, name='admin.overview'),
            U(r'/projects/overview', project.AllOverviewHandler, name='projects.overview'),
        ]

        static_path = os.path.join(
            os.path.dirname(__file__), 'static'
        )
        template_path = os.path.join(
            os.path.dirname(__file__), 'template'
        )

        ui_modules = {
            'Form': FormUIModule,
        }

        super(Application, self).__init__(
            handlers,
            static_path=static_path,
            template_path=template_path,
            login_url='/admin/login',
            ui_modules=ui_modules,
            **kwargs
        )


class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')
