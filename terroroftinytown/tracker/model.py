# encoding=utf-8
import base64
import hmac
import os
from rom import Model
from rom.columns import Text, Float, Json, Boolean, ManyToOne, DateTime, Integer
import datetime


class User(Model):
    '''User accounts that manager the tracker.'''
    username = Text(required=True, unique=True, index=True, prefix=True)
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
        return User.query.startswith(username='').count() == 0


class Project(Model):
    '''Project settings.'''
    name = Text(required=True, unique=True, index=True, prefix=True)
    min_version = Text()
    alphabet = Text()
    url_template = Text()
    rate_limit = Float()
    redirect_codes = Json()
    no_redirect_codes = Json()
    unavailable_codes = Json()
    banned_codes = Json()
    body_regex = Text()
    custom_code_required = Boolean()
    max_items = Integer()


class Queue(Model):
    '''The lower and upper bounds on the current sequence numbers.'''
    project = ManyToOne('Project', required=True)
    lower_sequence_num = Integer(required=True)
    upper_sequence_num = Integer(required=True)


class Claim(Model):
    '''A item checked out by a user.'''
    project = ManyToOne('Project', required=True)
    sequence_num = Integer(required=True)
    datetime_claimed = DateTime(
        default=datetime.datetime.utcnow()
    )
    tamper_key = Text()
    username = Text()
    ip_address = Text()


TODO_SET_KEY = 'TODO:{project_id}'
'''A set containing sequence numbers. Used for atomic checkouts.'''


def make_hash(plaintext, salt):
    key = salt.encode('ascii')
    msg = plaintext.encode('ascii')

    return hmac.new(key, msg).hexdigest().lower()


def new_salt():
    salt = os.urandom(16)
    return base64.b16encode(salt).decode('ascii').lower()
