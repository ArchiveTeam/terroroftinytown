# encoding=utf-8
import os.path

import tornado.web

from terroroftinytown.tracker.model import User


ACCOUNT_COOKIE_NAME = 'tottu'
ACCOUNT_TOKEN_COOKIE_NAME = 'tottt'


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        username_raw = self.get_secure_cookie(ACCOUNT_COOKIE_NAME)
        token = self.get_secure_cookie(ACCOUNT_TOKEN_COOKIE_NAME)

        if username_raw and token:
            username = username_raw.decode('ascii')

            if username:
                return User.check_account_session(username, token)

    def prepare(self):
        sentinel_path = self.application.settings.get('maintenance_sentinel')

        if sentinel_path and os.path.exists(sentinel_path):
            self._show_maintenance_page()

    def _show_maintenance_page(self):
        self.set_status(512, 'EXPORTING OUR SHIT')
        self.render('maintenance.html')
        raise tornado.web.Finish()
