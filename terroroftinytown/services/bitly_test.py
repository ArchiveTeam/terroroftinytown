import unittest

from terroroftinytown.services.bitly import Bitly6Service
from terroroftinytown.services.registry import registry


class TestBitly(unittest.TestCase):
    def test_registry(self):
        self.assertTrue('bitly' in registry)
        self.assertTrue('bitly_6' in registry)

    def test_6(self):
        service = Bitly6Service({'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'})

        self.assertEqual('I_H8U0', service.transform_sequence_num(0))
        self.assertEqual('FiGaOx', service.transform_sequence_num(10))
