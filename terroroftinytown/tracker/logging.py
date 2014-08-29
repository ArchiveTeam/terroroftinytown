import gzip
from logging.handlers import RotatingFileHandler
import os
import shutil


class GzipRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False):
        RotatingFileHandler.__init__(
            self, filename, mode=mode, maxBytes=maxBytes,
            backupCount=backupCount, encoding=encoding, delay=delay)
        self.rotator = self._rotator

    def _rotator(self, source, dest):
        with gzip.open(dest, 'wb') as gzip_file, \
                open(source, 'rb') as source_file:
            shutil.copyfileobj(source_file, gzip_file)

        os.remove(source)
