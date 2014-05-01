# encoding=utf-8
import redis
import rom.util

from terroroftinytown.tracker.model import User, Project, \
    BLOCKED_USERNAMES_SET_KEY


class Database(object):
    def __init__(self, host='localhost', port=6379, db=0):
        self._connection = redis.StrictRedis(
            host=host, port=port, db=db, decode_responses=True
        )
        rom.util.set_connection_settings(host=host, port=port, db=db)
        rom.util.refresh_indices(User)
        rom.util.refresh_indices(Project)

    @property
    def connection(self):
        return self._connection

    def block_username(self, username):
        self._connection.sadd(BLOCKED_USERNAMES_SET_KEY, username)

    def unblock_username(self, username):
        self._connection.srem(BLOCKED_USERNAMES_SET_KEY, username)

    def is_username_blocked(self, username):
        return self._connection.sismember(BLOCKED_USERNAMES_SET_KEY, username)

    def all_blocked_usernames(self):
        return self._connection.smembers(BLOCKED_USERNAMES_SET_KEY)
