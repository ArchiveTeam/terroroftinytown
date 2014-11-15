import unittest

from terroroftinytown.services.isgd import Isgd6Service
from terroroftinytown.services.registry import registry


class TestIsgd(unittest.TestCase):
    def test_registry(self):
        self.assertTrue('isgd' in registry)
        self.assertTrue('isgd_6' in registry)

    def test_6(self):
        service = Isgd6Service({'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'})

        self.assertEqual('Ph09LO', service.transform_sequence_num(0))
        self.assertEqual('h21rxr', service.transform_sequence_num(10))
