# encoding=utf-8
import os
import redis
import base64
import hmac


class Keys(object):
    usernames_set = 'usernames'
    user_hash = 'user:{0}'
    project_names_set = 'projects'
    project_hash = 'project:{0}'


class Database(object):
    def __init__(self, host='localhost', port=6379, db=0):
        self._connection = redis.StrictRedis(
            host=host, port=port, db=db, decode_responses=True
        )

    def is_username_exists(self, username):
        return self._connection.sismember(Keys.usernames_set, username)

    def is_no_users(self):
        return self._connection.scard(Keys.usernames_set) == 0

    def all_usernames(self):
        return self._connection.smembers(Keys.usernames_set)

    def add_user(self, username, password):
        salt = new_salt()

        self._connection.hset(
            Keys.user_hash.format(username),
            'hash', make_hash(password, salt)
        )
        self._connection.hset(
            Keys.user_hash.format(username),
            'salt', salt
        )

        self._connection.sadd(Keys.usernames_set, username)

    def remove_user(self, username):
        self._connection.srem(Keys.usernames_set, username)
        self._connection.delete(Keys.user_hash.format(username))

    def is_valid_user(self, username, password):
        hash_value = self._connection.hget(
            Keys.user_hash.format(username), 'hash'
        )
        salt_value = self._connection.hget(
            Keys.user_hash.format(username), 'salt'
        )

        if not hash_value:
            return

        test_hash = make_hash(password, salt_value)

        return all([a == b for a, b in zip(hash_value, test_hash)])

    def all_projects(self):
        return self._connection.smembers(Keys.project_names_set)


def make_hash(plaintext, salt):
    key = salt.encode('ascii')
    msg = plaintext.encode('ascii')

    return hmac.new(key, msg).hexdigest().lower()


def new_salt():
    salt = os.urandom(16)
    return base64.b16encode(salt).decode('ascii').lower()
