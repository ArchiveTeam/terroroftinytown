'''Test supervisor export and upload.'''
import os.path
import subprocess
import sys
import time
import unittest

from terroroftinytown.test.random_result import MockResult, MockProject


class TestExport(unittest.TestCase):
    @unittest.skip
    def test_supervisor(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'tracker', 'tracker_unittest.conf')

        project_boot = MockProject(delete_everything='yes-really!')
        project_boot.start(
            args=[config_path, '--count', '10'],
            )

        shortcode_boot = MockResult()
        shortcode_boot.start(
            args=[config_path, '--count', '100000', '--projects', '10'],
            )

        export_dir = '/tmp/tinytown_test_export{0}/'.format(int(time.time()))

        result = subprocess.run([
            sys.executable,
            '-m', 'terroroftinytown.release.supervisor',
            config_path,
            export_dir,
            '--verbose'
        ])

        self.assertEqual(result.returncode, 0)
