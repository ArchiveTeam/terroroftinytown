import unittest
from terroroftinytown.util.externalsort import GNUExternalSort


class TestExternalSort(unittest.TestCase):
    def test_gnu_sort(self):
        sorter = GNUExternalSort()
        sorter.input_many([
            ('00', 1),
            ('0', 2),
        ])
        sorter.input('11', 3)
        sorter.input('1', 4)

        results = tuple(sorter.sort())

        self.assertEqual(
            (
                ('0', 2),
                ('1', 4),
                ('00', 1),
                ('11', 3),
            ),
            results
        )
