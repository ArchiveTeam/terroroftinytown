# encoding=utf-8
'''Formatting URL data into old URLTeam format.'''

from terroroftinytown.format.base import *
from terroroftinytown.format.beacon import *

__all__ = ['UrlTeamWriter']

class UrlTeamWriter(BEACONWriter):
    def write_header(self, *args, **kwargs):
        pass

registry['urlteam'] = UrlTeamWriter