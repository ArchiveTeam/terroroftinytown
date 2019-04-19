from __future__ import unicode_literals

from terroroftinytown.services.adjix import AdjixService
from terroroftinytown.services.awesm import AwesmService
from terroroftinytown.services.base import DefaultService
from terroroftinytown.services.bitly import BitlyService, Bitly6Service
from terroroftinytown.services.feedly import FeedlyService, Feedly8Service
from terroroftinytown.services.isgd import IsgdService, Isgd6Service
from terroroftinytown.services.myspac import MyspAcService
from terroroftinytown.services.owly import OwlyService
from terroroftinytown.services.sharedby import SharedBy6Service, SharedByService
from terroroftinytown.services.shares import SharesService
from terroroftinytown.services.snipurl import SnipurlService
from terroroftinytown.services.tighturl import TighturlService
from terroroftinytown.services.tinyurl import TinyurlService, Tinyurl7Service
from terroroftinytown.services.vgd import VgdService, Vgd6Service
from terroroftinytown.services.vitrue import VitrueService
from terroroftinytown.services.xco import XCOService
from terroroftinytown.services.yatuc import YatucService
from terroroftinytown.services.alturl import AlturlService
from terroroftinytown.services.tinyurlhu import TinyurlHu4Service,\
    TinyurlHuService
from terroroftinytown.services.googl import GooglService


registry = {}
'''Mapping of unicode strings to BaseService classes.'''


registry['_default'] = DefaultService
registry['isgd'] = IsgdService
registry['isgd_6'] = Isgd6Service
registry['vgd'] = VgdService
registry['vgd_6'] = Vgd6Service
registry['bitly'] = BitlyService
registry['bitly_6'] = Bitly6Service
registry['xco'] = XCOService
registry['pub-vitrue-com'] = VitrueService
registry['tighturl-com'] = TighturlService
registry['tinyurl'] = TinyurlService
registry['tinyurl_7'] = Tinyurl7Service
registry['adjix'] = AdjixService
registry['yatuc'] = YatucService
registry['shar-es'] = SharesService
registry['feedly'] = FeedlyService
registry['feedly_8'] = Feedly8Service
registry['awe-sm'] = AwesmService
registry['ow-ly'] = OwlyService
registry['snipurl'] = SnipurlService
registry['snipurl_range2'] = SnipurlService
registry['sharedby-co'] = SharedByService
registry['sharedby-co_6'] = SharedBy6Service
registry['mysp-ac'] = MyspAcService
registry['alturl-com'] = AlturlService
registry['tinyurl-hu'] = TinyurlHuService
registry['tinyurl-hu_4'] = TinyurlHu4Service
registry['goo-gl'] = GooglService
