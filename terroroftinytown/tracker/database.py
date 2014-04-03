# encoding=utf-8
import redis
import rom.util

from terroroftinytown.tracker.model import User, Project


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
