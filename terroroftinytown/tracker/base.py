# encoding=utf-8
import tornado.web

ACCOUNT_COOKIE_NAME = 'tottu'


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        username = self.get_secure_cookie(ACCOUNT_COOKIE_NAME)

        if self.application.db.is_username_exists(username):
            return username
        elif self.application.db.is_no_users():
            return username
