# encoding=utf-8
'''Formatting URL data into the BEACON format.'''

from datetime import datetime
from terroroftinytown.format.base import *

__all__ = ['BEACONWriter']

class BEACONWriter(BaseWriter):
    homepage = 'http://urlte.am/'

    def write_header(self, site, *args, **kwargs):
        self.fp.write('#FORMAT: BEACON\n'.encode('ascii'))
        self.fp.write(('#PREFIX: %s\n' % (site)).encode('ascii'))

        if self.homepage:
            self.fp.write(('#HOMEPAGE: %s\n' % (self.homepage)).encode('ascii'))

        timestamp = datetime.utcnow()
        if 'timestamp' in kwargs:
            assert isinstance('timestamp', datetime), \
                'timestamp argument must be datetime instance'
            timestamp = kwargs['timestamp']
        self.fp.write(('#TIMESTAMP: %s\n' % (timestamp.isoformat())).encode('ascii'))

        self.fp.write(b'\n')

    def write_shortcode(self, shortcode, url, encoding):
        self.fp.write(shortcode.encode('ascii'))
        self.fp.write(b'|')
        self.fp.write(url.encode(encoding))
        self.fp.write(b'\n')

registry['beacon'] = BEACONWriter
