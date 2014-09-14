
from terroroftinytown.services.base import DefaultService
from terroroftinytown.services.isgd import IsgdService
from terroroftinytown.six import u
from terroroftinytown.services.bitly import BitlyService


registry = {}
'''Mapping of unicode strings to BaseService classes.'''


registry[u('_default')] = DefaultService
registry[u('isgd')] = IsgdService
registry[u('bitly')] = BitlyService
