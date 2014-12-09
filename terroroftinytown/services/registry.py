from __future__ import unicode_literals

from terroroftinytown.services.base import DefaultService
from terroroftinytown.services.isgd import IsgdService, Isgd6Service
from terroroftinytown.services.bitly import BitlyService, Bitly6Service
from terroroftinytown.services.xco import XCOService
from terroroftinytown.services.vitrue import VitrueService
from terroroftinytown.services.tighturl import TighturlService
from terroroftinytown.services.tinyurl import TinyurlService, Tinyurl7Service
from terroroftinytown.services.adjix import AdjixService


registry = {}
'''Mapping of unicode strings to BaseService classes.'''


registry['_default'] = DefaultService
registry['isgd'] = IsgdService
registry['isgd_6'] = Isgd6Service
registry['bitly'] = BitlyService
registry['bitly_6'] = Bitly6Service
registry['xco'] = XCOService
registry['pub-vitrue-com'] = VitrueService
registry['tighturl-com'] = TighturlService
registry['tinyurl'] = TinyurlService
registry['tinyurl_7'] = Tinyurl7Service
registry['adjix'] = AdjixService
