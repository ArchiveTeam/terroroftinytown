import unittest

from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin


class MockService(HashRandMixin, BaseService):
    def get_shortcode_width(self):
        return 4


class TestRand(unittest.TestCase):
    def test_hash_rand_mixin(self):
        params = {
            'alphabet': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        }

        service = MockService(params)

        self.assertEqual('kYpa', service.transform_sequence_num(0))
        self.assertEqual('vENp', service.transform_sequence_num(1))
