from __future__ import unicode_literals

from terroroftinytown.services.base import DefaultService
from terroroftinytown.services.isgd import IsgdService
from terroroftinytown.services.bitly import BitlyService
from terroroftinytown.services.xco import XCOService
from terroroftinytown.services.vitrue import VitrueService
from terroroftinytown.services.tighturl import TighturlService
from terroroftinytown.services.tinyurl import TinyurlService


registry = {}
'''Mapping of unicode strings to BaseService classes.'''


registry['_default'] = DefaultService
registry['isgd'] = IsgdService
registry['bitly'] = BitlyService
registry['xco'] = XCOService
registry['pub-vitrue-com'] = VitrueService
registry['tighturl-com'] = TighturlService
registry['tinyurl'] = TinyurlService
