# encoding=utf-8
import tornado.web

from terroroftinytown.tracker.model import User


ACCOUNT_COOKIE_NAME = 'tottu'


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        username = self.get_secure_cookie(ACCOUNT_COOKIE_NAME)

        if username:
            user = User.get_by(username=username)

            if user:
                return user.username
            elif User.no_users_exist():
                return username
