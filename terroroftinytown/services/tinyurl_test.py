import unittest

from terroroftinytown.services.registry import registry
from terroroftinytown.services.tinyurl import Tinyurl7Service


class TestTinyurl(unittest.TestCase):
    def test_registry(self):
        self.assertTrue('tinyurl' in registry)
        self.assertTrue('tinyurl_7' in registry)

    def test_7(self):
        service = Tinyurl7Service({'alphabet': '0123456789abcdefghijklmnopqrstuvwxyz'})

        self.assertEqual('kua854w', service.transform_sequence_num(0))
        self.assertEqual('m8o5129', service.transform_sequence_num(10))
