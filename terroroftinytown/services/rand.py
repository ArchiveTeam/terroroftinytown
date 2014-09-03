'''Instead of sequential shortcodes, generate pseudorandom shortcodes.

See https://github.com/ArchiveTeam/tinyback/blob/master/tinyback/generators.py
for historical details.
'''
import hashlib
import struct
from terroroftinytown.client import alphabet


class BaseRandMixin:
    def get_shortcode_width(self):
        '''Return the number of characters the shortcode string.'''
        raise NotImplementedError('Please override me with an integer.')


class LegacyChainMixin(BaseRandMixin):
    def transform_sequence_num(self, sequence_num):
        # TODO: write me
        raise NotImplementedError('todo: not yet implemented')


class HashRandMixin(BaseRandMixin):
    def transform_sequence_num(self, sequence_num):
        seed = struct.pack('>Q', sequence_num)
        hasher = hashlib.md5(seed)
        digest = hasher.digest()
        num = struct.unpack('>Q', digest[:8])[0]
        shortcode = alphabet.int_to_str(num, self.params['alphabet'])
        shortcode = shortcode[:self.get_shortcode_width()]

        return shortcode
