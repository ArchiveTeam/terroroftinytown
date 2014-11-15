import itertools
import unittest

from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
import collections


class MockService(HashRandMixin, BaseService):
    def __init__(self, *args, **kwargs):
        self.shortcode_width = kwargs.pop('shortcode_width', 4)
        BaseService.__init__(self, *args, **kwargs)

    def get_shortcode_width(self):
        return self.shortcode_width


class TestRand(unittest.TestCase):
    def test_hash_rand_mixin(self):
        params = {
            'alphabet': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        }

        service = MockService(params)

        self.assertEqual('TXMa', service.transform_sequence_num(0))
        self.assertEqual('lv0q', service.transform_sequence_num(1))


if __name__ == '__main__':
    for width in (1, 2, 3, 4, 5, 6, 7, 8):
        service = MockService(
            {
                'alphabet': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            },
            shortcode_width=width
        )

        distributions = [collections.Counter() for dummy in range(width)]

        for num in itertools.count():
            shortcode = service.transform_sequence_num(num)

            for index, char in enumerate(shortcode):
                distributions[index][char] += 1

            if num > 100000:
                break

        print(width)
        print(distributions)
