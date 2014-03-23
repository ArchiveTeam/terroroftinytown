# encoding=utf-8
import os.path
from tornado.web import URLSpec as U
import tornado.web

from terroroftinytown.tracker import account, admin, project, api
from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.ui import FormUIModule


class Application(tornado.web.Application):
    def __init__(self, database, **kwargs):
        self.db = database

        handlers = [
            U(r'/', IndexHandler),
            U(r'/admin/', admin.AdminHandler, name='admin.overview'),
            U(r'/admin/login', account.LoginHandler, name='admin.login'),
            U(r'/admin/logout', account.LogoutHandler, name='admin.logout'),
            U(r'/users/', account.AllUsersHandler, name='users.overview'),
            U(r'/user/([a-z0-9_-]*)', account.UserHandler, name='user.overview'),
            U(r'/projects/overview', project.AllProjectsHandler, name='projects.overview'),
            U(r'/project/([a-z0-9_-]*)', project.ProjectHandler, name='project.overview'),
            U(r'/project/([a-z0-9_-]*)/queue', project.QueueHandler, name='project.queue'),
            U(r'/project/([a-z0-9_-]*)/claims', project.ClaimsHandler, name='project.claims'),
            U(r'/project/([a-z0-9_-]*)/blocked', project.BlockedHandler, name='project.blocked'),
            U(r'/project/([a-z0-9_-]*)/settings', project.SettingsHandler, name='project.settings'),
            U(r'/project/([a-z0-9_-]*)/delete', project.DeleteHandler, name='project.delete'),
            U(r'/api/live_stats', api.LiveStatsHandler, name='api.live_stats'),
            U(r'/api/project_settings', api.ProjectSettingsHandler, name='api.project_settings'),
            U(r'/api/get', api.GetHandler, name='api.get'),
            U(r'/api/done', api.DoneHandler, name='api.done'),
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
