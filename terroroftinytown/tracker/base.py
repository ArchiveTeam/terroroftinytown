# encoding=utf-8
from sqlalchemy.exc import SQLAlchemyError
import tornado.web

from terroroftinytown.tracker.model import User


ACCOUNT_COOKIE_NAME = 'tottu'


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        username_raw = self.get_secure_cookie(ACCOUNT_COOKIE_NAME)

        if username_raw:
            username = username_raw.decode('ascii')

            if username:
                if User.is_user_exists(username):
                    return username
