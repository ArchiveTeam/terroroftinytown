'''Test exporting.'''
import os.path
import unittest

from terroroftinytown.tracker.export import ExporterBootstrap, Exporter
from terroroftinytown.test.random_result import MockResult, MockProject
import functools


class TestExport(unittest.TestCase):
    def test_beacon(self):
        config_path = os.path.join(os.path.dirname(__file__), 'tracker_unittest.conf')

        project_boot = MockProject(delete_everything='yes-really!')
        project_boot.start(
            args=[config_path, '--count', '10'],
            )

        shortcode_boot = MockResult()
        shortcode_boot.start(
            args=[config_path, '--count', '100000', '--projects', '10'],
            )

        boot = ExporterBootstrap()
        args = [
            config_path, '--format', 'beacon',
            '--include-settings', '--zip',
            '--dir-length', '0', '--file-length', '0', '--max-right', '8',
            '--delete',
            '/tmp/tinytown_test_export/',
            ]
        boot.start(args=args)

    def test_split_shortcode(self):
        split = functools.partial(
            Exporter.split_shortcode,
            dir_length=2, max_right=4, file_length=2)

        self.assertEqual(
            ([], '', 'a'),
            split('a')
        )
        self.assertEqual(
            ([], '', 'ab'),
            split('ab')
        )
        self.assertEqual(
            ([], '', 'abc'),
            split('abc')
        )
        self.assertEqual(
            ([], '', 'abcd'),
            split('abcd')
        )
        self.assertEqual(
            ([], 'a', 'bcde'),
            split('abcde')
        )
        self.assertEqual(
            ([], 'ab', 'cdef'),
            split('abcdef')
        )
        self.assertEqual(
            (['ab'], 'abc', 'defg'),
            split('abcdefg')
        )
        self.assertEqual(
            (['ab'], 'abcd', 'efgh'),
            split('abcdefgh')
        )
        self.assertEqual(
            (['ab', 'cd'], 'abcde', 'fghi'),
            split('abcdefghi')
        )
        self.assertEqual(
            (['ab', 'cd'], 'abcdef', 'ghij'),
            split('abcdefghij')
        )
        self.assertEqual(
            (['ab', 'cd', 'ef'], 'abcdefg', 'hijk'),
            split('abcdefghijk')
        )

    def test_split_shortcode_2(self):
        split = functools.partial(
            Exporter.split_shortcode,
            dir_length=1, max_right=6, file_length=1)

        self.assertEqual(
            ([], '', 'a'),
            split('a')
        )
        self.assertEqual(
            ([], '', 'ab'),
            split('ab')
        )
        self.assertEqual(
            ([], '', 'abc'),
            split('abc')
        )
        self.assertEqual(
            ([], '', 'abcd'),
            split('abcd')
        )
        self.assertEqual(
            ([], '', 'abcde'),
            split('abcde')
        )
        self.assertEqual(
            ([], '', 'abcdef'),
            split('abcdef')
        )
        self.assertEqual(
            ([], 'a', 'bcdefg'),
            split('abcdefg')
        )
        self.assertEqual(
            (['a'], 'ab', 'cdefgh'),
            split('abcdefgh')
        )
        self.assertEqual(
            (['a', 'b'], 'abc', 'defghi'),
            split('abcdefghi')
        )
        self.assertEqual(
            (['a', 'b', 'c'], 'abcd', 'efghij'),
            split('abcdefghij')
        )
        self.assertEqual(
            (['a', 'b', 'c', 'd'], 'abcde', 'fghijk'),
            split('abcdefghijk')
        )

    def test_split_shortcode_3(self):
        split = functools.partial(
            Exporter.split_shortcode,
            dir_length=0, max_right=6, file_length=1)

        self.assertEqual(
            ([], '', 'a'),
            split('a')
        )
        self.assertEqual(
            ([], 'abcde', 'fghijk'),
            split('abcdefghijk')
        )

    def test_split_shortcode_4(self):
        split = functools.partial(
            Exporter.split_shortcode,
            dir_length=0, max_right=6, file_length=0)

        self.assertEqual(
            ([], '', 'a'),
            split('a')
        )
        self.assertEqual(
            ([], 'abcde', 'fghijk'),
            split('abcdefghijk')
        )

    def test_split_shortcode_5(self):
        split = functools.partial(
            Exporter.split_shortcode,
            dir_length=0, max_right=0, file_length=0)

        self.assertEqual(
            ([], 'a', ''),
            split('a')
        )
        self.assertEqual(
            ([], 'abcdefghijk', ''),
            split('abcdefghijk')
        )
