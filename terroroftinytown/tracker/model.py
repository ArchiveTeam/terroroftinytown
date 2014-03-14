# encoding=utf-8
import base64
import hmac
import os
from rom import Model
from rom.columns import Text


class User(Model):
    username = Text(required=True, unique=True, index=True)
    salt = Text()
    hash = Text()

    def set_password(self, password):
        self.salt = new_salt()
        self.hash = make_hash(password, self.salt)

    def check_password(self, password):
        test_hash = make_hash(password, self.salt)

        return all([a == b for a, b in zip(self.hash, test_hash)])

    @classmethod
    def no_users_exist(cls):
        # DERP: https://github.com/josiahcarlson/rom/issues/12
        print(User.query.order_by('username').count())
        return User.query.order_by('username').count() == 0


class Project(Model):
    name = Text(required=True, unique=True, index=True)
    alphabet = Text()


def make_hash(plaintext, salt):
    key = salt.encode('ascii')
    msg = plaintext.encode('ascii')

    return hmac.new(key, msg).hexdigest().lower()


def new_salt():
    salt = os.urandom(16)
    return base64.b16encode(salt).decode('ascii').lower()
