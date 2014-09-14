
from terroroftinytown.services.base import DefaultService
from terroroftinytown.services.isgd import IsgdService
from terroroftinytown.six import u


registry = {}
'''Mapping of unicode strings to BaseService classes.'''


registry[u('_default')] = DefaultService
registry[u('isgd')] = IsgdService
