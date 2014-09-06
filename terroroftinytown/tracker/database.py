# encoding=utf-8
import sqlalchemy
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import SingletonThreadPool

from terroroftinytown.tracker.model import Session, Base


class Database(object):
    def __init__(self, path, delete_everything=False):
        if path.startswith('sqlite:'):
            self.engine = create_engine(path, poolclass=SingletonThreadPool)
            sqlalchemy.event.listen(
                self.engine, 'connect', self._apply_pragmas_callback)
        else:
            self.engine = create_engine(path)

        Session.configure(bind=self.engine)

        if delete_everything == 'yes-really!':
            self._delete_everything()

        Base.metadata.create_all(self.engine)

    @classmethod
    def _apply_pragmas_callback(cls, connection, record):
        connection.execute('PRAGMA journal_mode=WAL')

    def _delete_everything(self):
        Base.metadata.drop_all(self.engine)
