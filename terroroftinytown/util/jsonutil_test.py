# encoding=utf-8
from __future__ import unicode_literals

import json
import unittest

from terroroftinytown.util.jsonutil import NativeStringJSONEncoder, \
    NativeStringJSONDecoder


class Test(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(
            '"5C5C7830305C5C61"',
            json.dumps(r'\x00\a', cls=NativeStringJSONEncoder)
        )
        self.assertEqual(
            '"5C7866305C553030303166346565"',
            json.dumps('ð📮', cls=NativeStringJSONEncoder)
        )

    def test_decode(self):
        self.assertEqual(
            r'\x00\a',
            json.loads(r'"5C5C7830305C5C61"', cls=NativeStringJSONDecoder)
        )
        self.assertEqual(
            'ð📮',
            json.loads(r'"5C7866305C553030303166346565"',
                       cls=NativeStringJSONDecoder)
        )
