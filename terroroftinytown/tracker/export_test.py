'''Test exporting.'''
import functools
import lzma
import os.path
import time
import unittest
import zipfile

from terroroftinytown.test.random_result import MockResult, MockProject
from terroroftinytown.tracker.export import ExporterBootstrap, Exporter


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

        export_dir = '/tmp/tinytown_test_export{0}/'.format(int(time.time()))

        boot = ExporterBootstrap()
        args = [
            config_path, '--format', 'beacon',
            '--include-settings', '--zip',
            '--dir-length', '0', '--file-length', '0', '--max-right', '8',
            '--delete',
            export_dir,
            ]
        boot.start(args=args)

        count = 0

        for filename in os.listdir(export_dir):
            print('filename', filename)
            with zipfile.ZipFile(os.path.join(export_dir, filename), 'r') as zip_file:
                for name in zip_file.namelist():
                    print(' name', name)

                    if not name.endswith('.txt.xz'):
                        continue

                    in_file = zip_file.open(name)
                    is_prefix = False

                    for line in lzma.LZMAFile(in_file):
                        if line.startswith(b'#'):
                            if b'PREFIX' in line:
                                is_prefix = True

                                # Check if "{shortcode}" was accidentally replaced out
                                self.assertNotIn(b'//', line.replace(b'http://', b''))

                            continue

                        line = line.strip()
                        if line:
                            count += 1

                            self.assertGreaterEqual(line.index(b'|'), 1)

                            if is_prefix:
                                self.assertFalse(line.startswith(b'http'))
                            else:
                                self.assertTrue(line.startswith(b'http'))

                    in_file.close()

        self.assertEqual(100000, count)

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
