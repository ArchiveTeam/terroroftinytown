'''External Sorting'''
import tempfile
import base64
import pickle
import subprocess


class GNUExternalSort(object):
    def __init__(self, temp_prefix='tott', temp_dir=None):
        self._temp_file = tempfile.NamedTemporaryFile(
            prefix=temp_prefix, dir=temp_dir
        )
        self.rows = 0

    def input(self, key, value):
        self.input_many([(key, value)])

    def input_many(self, key_values):
        for key, value in key_values:
            assert ' ' not in key
            self._temp_file.write(str(len(key)).encode('ascii'))
            self._temp_file.write(b' ')
            self._temp_file.write(key.encode('ascii'))
            self._temp_file.write(b' ')
            self._temp_file.write(base64.b64encode(pickle.dumps(value)))
            self._temp_file.write(b'\n')

            self.rows += 1

    def sort(self):
        self._temp_file.flush()

        proc = subprocess.Popen(
            [
                'sort', self._temp_file.name,
                '--key', '1,1n', '--key', '2,2', '--key', '3,3',
                '--unique',
            ],
            stdout=subprocess.PIPE,
            env={'LC_COLLATE': 'C', 'LC_ALL': 'C'},
        )

        for line in proc.stdout:
            key_len, key, serialized_value = line.split(None, 2)
            key = key.decode('ascii')
            value = pickle.loads(base64.b64decode(serialized_value))

            yield key, value

        proc.communicate()

        if proc.returncode:
            raise OSError(
                'Sort subprocess exited with {0}.'.format(proc.returncode)
            )

        self._temp_file.close()
