import base64
import json
from collections import Sequence, Mapping

import terroroftinytown.six


class NativeStringJSONDecoder(json.JSONDecoder):
    '''JSON decoder that channels unicode strings.'''
    def decode(self, s, **kwargs):
        result = json.JSONDecoder.decode(self, s, **kwargs)

        return self.channel_unicode(result)

    @classmethod
    def channel_unicode(cls, o):
        # http://stackoverflow.com/a/6415359/1524507
        if isinstance(o, terroroftinytown.six.string_types):
            if isinstance(o, terroroftinytown.six.text_type):
                o = o.encode('ascii')
            return base64.b16decode(o).decode('unicode_escape')
        elif isinstance(o, Sequence):
            return [cls.channel_unicode(item) for item in o]
        elif isinstance(o, Mapping):
            return dict((key, cls.channel_unicode(value))
                        for key, value in o.items())
        else:
            return o


class NativeStringJSONEncoder(json.JSONEncoder):
    '''JSON encoder that channels unicode strings.'''
    def encode(self, o):
        o = self.channel_unicode(o)

        return json.JSONEncoder.encode(self, o)

    @classmethod
    def channel_unicode(cls, o):
        # http://stackoverflow.com/a/6415359/1524507
        if isinstance(o, (terroroftinytown.six.binary_type,
                          terroroftinytown.six.string_types)):
            if isinstance(o, terroroftinytown.six.binary_type):
                o = o.decode('latin1')
            o = base64.b16encode(o.encode('unicode_escape')).decode('ascii')
            return o
        elif isinstance(o, Sequence):
            return [cls.channel_unicode(item) for item in o]
        elif isinstance(o, Mapping):
            return dict((key, cls.channel_unicode(value))
                        for key, value in o.items())
        else:
            return o
