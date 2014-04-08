import unittest

from terroroftinytown.client.alphabet import int_to_str, str_to_int


class Test(unittest.TestCase):
    def test_int_to_str(self):
        self.assertEqual('a', int_to_str(0, 'abcde'))
        self.assertEqual('1E0F3', int_to_str(123123, '0123456789ABCDEF'))
        self.assertEqual('w1R', int_to_str(123123, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))

    def test_str_to_int(self):
        self.assertEqual(0, str_to_int('a', 'abcde'))
        self.assertEqual(123123, str_to_int('1E0F3', '0123456789ABCDEF'))
        self.assertEqual(123123, str_to_int('w1R', '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
