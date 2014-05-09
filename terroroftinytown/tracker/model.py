# encoding=utf-8
import base64
import datetime
import hmac
import os

from rom import Model
from rom.columns import Text, Float, Json, Boolean, ManyToOne, DateTime, Integer
import rom.util


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

        if len(self.hash) != len(test_hash):
            return False

        iterable = [a == b for a, b in zip(self.hash, test_hash)]
        ok = True

        for result in iterable:
            ok &= result

        return ok

    @classmethod
    def no_users_exist(cls):
        return User.query.startswith(username='').count() == 0

    @classmethod
    def all_usernames(cls):
        users = cls.query.startswith(username='').all()
        return [user.username for user in users]


class Project(Model):
    '''Project settings.'''
    name = Text(required=True, unique=True, index=True, prefix=True)
    min_version = Text()
    alphabet = Text(default='0123456789abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    url_template = Text(default='http://example.com/{shortcode}')
    request_delay = Float(default=0.5)
    redirect_codes = Json(default=[301, 302, 303, 307])
    no_redirect_codes = Json(default=[404])
    unavailable_codes = Json(default=[200])
    banned_codes = Json(default=[420])
    body_regex = Text()
    custom_code_required = Boolean()
    method = Text(default='head')

    enabled = Boolean(default=True)
    autoqueue = Boolean()
    num_count_per_item = Integer(default=50, required=True)
    max_num_items = Integer(default=1000, required=True)
    lower_sequence_num = Integer(default=0, required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min_version': self.min_version,
            'alphabet': self.alphabet,
            'url_template': self.url_template,
            'request_delay': self.request_delay,
            'redirect_codes': self.redirect_codes,
            'no_redirect_codes': self.no_redirect_codes,
            'unavailable_codes': self.unavailable_codes,
            'banned_codes': self.banned_codes,
            'body_regex': self.body_regex,
            'custom_code_required': self.custom_code_required,
            'method': self.method,
        }

    @classmethod
    def all_project_names(cls):
        projects = cls.query.startswith(name='').all()
        return [project.name for project in projects]


class Claim(Model):
    '''A item checked out by a user.'''
    project = ManyToOne('Project', required=True)
    lower_sequence_num = Integer(required=True)
    upper_sequence_num = Integer(required=True)
    datetime_claimed = DateTime(
        default=datetime.datetime.utcnow()
    )
    tamper_key = Text()
    username = Text()
    ip_address = Text()

    def __init__(self, conn=None, **kwargs):
        Model.__init__(self, **kwargs)

        if conn:
            self._conn = conn

    def to_dict(self):
        return {
            'id': self.id,
            'project': self.project.to_dict(),
            'lower_sequence_num': self.lower_sequence_num,
            'upper_sequence_num': self.upper_sequence_num,
            'datetime_claimed': self.datetime_claimed,
            'tamper_key': self.tamper_key,
            'username': self.username,
            'ip_address': self.ip_address,
        }


class TodoQueue(object):
    '''A set containing strings of sequence number ranges.

    Used for atomic checkouts. Each member is formatted like NN-MM
    (ie: string representation of an integer, ascii hyphen, string
    representation of an integer.
    '''
    SET_KEY = 'TODO:{project_id}'

    @classmethod
    def clear(cls, project_id):
        connection = rom.util.get_connection()
        connection.delete(cls.SET_KEY.format(project_id=project_id))

    @classmethod
    def add_one(cls, project_id, lower_sequence_num, upper_sequence_num):
        connection = rom.util.get_connection()
        connection.sadd(
            cls.SET_KEY.format(project_id, project_id),
            '{0}-{1}'.format(lower_sequence_num, upper_sequence_num)
        )

    @classmethod
    def get_one(cls, project_id, connection=None):
        connection = connection or rom.util.get_connection()
        member = connection.spop(cls.SET_KEY.format(project_id=project_id))
        lower_num, upper_num = member.split('-')
        return lower_num, upper_num





class BlockedUsers(object):
    '''A set containing strings of IP addresses or usernames.'''
    SET_KEY = 'blocked_usernames'

    @classmethod
    def block_username(cls, username):
        connection = rom.util.get_connection()
        connection.sadd(cls.SET_KEY, username)

    @classmethod
    def unblock_username(cls, username):
        connection = rom.util.get_connection()
        connection.srem(cls.SET_KEY, username)

    @classmethod
    def is_username_blocked(cls, username):
        connection = rom.util.get_connection()
        return connection.sismember(cls.SET_KEY, username)

    @classmethod
    def all_blocked_usernames(cls):
        connection = rom.util.get_connection()
        return connection.smembers(cls.SET_KEY)


def make_hash(plaintext, salt):
    key = salt.encode('ascii')
    msg = plaintext.encode('ascii')

    return hmac.new(key, msg).hexdigest().lower()


def new_salt():
    salt = os.urandom(16)
    return base64.b16encode(salt).decode('ascii').lower()


def checkout_item(project_id, username, ip_address):
    connection = rom.util.get_connection()
    pipe = connection.pipeline()
    lower_num, upper_num = TodoQueue.get_one(project_id, connection=pipe)

    claim = Claim(
        conn=pipe,
        project=project_id,
        username=username,
        ip_address=ip_address,
        lower_sequence_num=lower_num,
        upper_sequence_num=upper_num,
    )

    claim.save()
    del claim._conn

    pipe.execute()

    return claim
