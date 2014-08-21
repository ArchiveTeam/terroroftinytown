# encoding=utf-8
'''Base class for format writers'''

import io

__all__ = ['BaseWriter', 'registry']

registry = {}

class BaseWriter:
    def __init__(self, fp, *args, **kwargs):
        assert isinstance(fp, io.BufferedIOBase)

        self.fp = fp

    def write_header(self, site, *args, **kwargs):
        '''Write file headers and metadata'''
        pass

    def write_shortcode(self, shortcode, url, encoding):
        raise NotImplementedError

    def write_footer(self, *args, **kwargs):
        '''Write file footer and metadata'''
        pass