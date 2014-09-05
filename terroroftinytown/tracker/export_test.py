'''Test exporting.'''
import os.path
import unittest

from terroroftinytown.tracker.export import ExporterBootstrap
from terroroftinytown.test.random_result import MockResult, MockProject


class TestExport(unittest.TestCase):
    def test_beacon(self):
        config_path = os.path.join(os.path.dirname(__file__), 'tracker_unittest.conf')

        shortcode_boot = MockResult()
        shortcode_boot.start(
            args=[config_path, '--count', '10000', '--projects', '10'],
            delete_everything='yes-really!')

        boot = ExporterBootstrap()
        args = [config_path, '--format', 'beacon', '/tmp/tinytown_test_export/']
        boot.start(args)

