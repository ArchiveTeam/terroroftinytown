'''Dump the SQLite and Redis db.'''
import gzip
import io
import json
import os.path
import subprocess

from terroroftinytown.tracker.bootstrap import Bootstrap
import shutil


class BackupBootstrap(Bootstrap):
    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        self.setup_redis()
        self.dump()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('dest_dir')

    def dump(self):
        if not self.config['database']['path'].startswith('sqlite:///'):
            raise Exception('Only SQLite is supported')

        if not os.path.isdir(self.args.dest_dir):
            raise Exception('Destination is not a directory.')

        filename = self.config['database']['path'].replace('sqlite:///', '')
        dump_filename = os.path.join(self.args.dest_dir, 'tinytown.sql.gz')
        temp_dump_filename = dump_filename + '-new'

        print('Begin db dump.', filename, dump_filename)

        with gzip.GzipFile(temp_dump_filename, mode='wb') as gzip_file:
            proc = subprocess.Popen(['sqlite3', filename, '.dump'],
                                    stdout=subprocess.PIPE)
            shutil.copyfileobj(proc.stdout, gzip_file)
            proc.communicate()

            if proc.returncode:
                raise Exception('Proc returned {}'.format(proc.returncode))

        os.rename(temp_dump_filename, dump_filename)
        print('Done')

        dump_filename = os.path.join(self.args.dest_dir, 'tinytown.redis.gz')
        temp_dump_filename = dump_filename + '-new'

        print('Begin redis dump', dump_filename)
        keys = self.redis.keys(self.config['redis'].get('prefix', '') + '*')
        data = {}

        for key in keys:
            data[key.decode('ascii')] = self.redis.dump(key).decode('latin-1')

        with gzip.GzipFile(temp_dump_filename, mode='wb') as gzip_file:
            json.dump(data, io.TextIOWrapper(gzip_file))

        os.rename(temp_dump_filename, dump_filename)

        print('Done')


if __name__ == '__main__':
    BackupBootstrap().start()
