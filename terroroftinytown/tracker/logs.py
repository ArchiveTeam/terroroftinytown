import gzip
from logging.handlers import TimedRotatingFileHandler
import os
import shutil


class LogFilter(object):
    def filter(self, record):
        if not record.name:
            return True
        if record.name == 'tornado.access':
            return False

        return True


class GzipTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=52,
                 encoding=None, delay=False, utc=False, atTime=None):
        TimedRotatingFileHandler.__init__(
            self, filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding,
            delay=delay, utc=utc, atTime=atTime
        )
        self.rotator = self._rotator

    def _rotator(self, source, dest):
        with gzip.open(dest, 'wb') as gzip_file, \
                open(source, 'rb') as source_file:
            shutil.copyfileobj(source_file, gzip_file)

        os.remove(source)
