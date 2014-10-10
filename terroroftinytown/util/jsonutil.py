import base64
import json

import terroroftinytown.six


class NativeStringJSONDecoder(json.JSONDecoder):
    '''JSON decoder that channels unicode strings.'''
    def decode(self, s, **kwargs):
        result = json.JSONDecoder.decode(self, s, **kwargs)

        if isinstance(result, terroroftinytown.six.string_types):
            if isinstance(result, terroroftinytown.six.text_type):
                result = result.encode('ascii')
            return base64.b16decode(result).decode('unicode_escape')
        else:
            return result


class NativeStringJSONEncoder(json.JSONEncoder):
    '''JSON encoder that channels unicode strings.'''
    def encode(self, o):
        if isinstance(o, terroroftinytown.six.string_types):
            if isinstance(o, terroroftinytown.six.binary_type):
                o = o.decode('ascii')
            o = base64.b16encode(o.encode('unicode_escape')).decode('ascii')

        return json.JSONEncoder.encode(self, o)
