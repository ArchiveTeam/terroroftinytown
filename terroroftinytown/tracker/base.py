# encoding=utf-8
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

            if username and User.check_account_session(username, token):
                return username

    def prepare(self):
        self.application.log_filter.username = self.get_current_user()
        if self.application.is_maintenance_in_progress():
            self._show_maintenance_page()

    def _show_maintenance_page(self):
        self.set_status(512, 'EXPORTING OUR SHIT')
        self.render('maintenance.html')
        raise tornado.web.Finish()
