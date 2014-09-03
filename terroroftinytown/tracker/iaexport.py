# encoding: utf-8

import os
import sys
import io
import lzma
import time
import boto

from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
from boto.exception import S3CreateError

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.export import Exporter

class IAExporter(Exporter):
    _last_filename = None
    _fp = None

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_format(self.config.get('iaexporter', 'format'))
        self.after = self.get_last_export()
        self.setup_boto()

    def dump(self):
        super().dump()
        self.write_last_export()

    def setup_boto(self):
        self.boto = boto.connect_s3(
            self.config.get('iaexporter', 'access_key'),
            self.config.get('iaexporter', 'secret_key'),
            host=self.config.get('iaexporter', 'endpoint'), 
            is_secure=False,
            calling_format=OrdinaryCallingFormat()
        )
        current_time = time.gmtime()
        bucket_name = self.config.get('iaexporter', 'item', vars={
            'year': '%02d'%(current_time[0]),
            'month': '%02d'%(current_time[1]),
            'day': '%02d'%(current_time[2]),
        })
        try:
            self.bucket = self.boto.create_bucket(bucket_name, {
                'x-archive-meta-collection': self.config.get('iaexporter', 'collection'),
                'x-archive-meta-mediatype': 'software',
                'x-archive-ignore-preexisting-bucket': '1'
            })
        except S3CreateError:
            self.bucket = self.boto.get_bucket(bucket_name)

    def get_last_export(self):
        filename = self.config.get('iaexporter', 'last_export_file')
        if os.path.isfile(filename):
            return open(filename).read()

    def make_output_dir(self):
        pass

    def get_fp(self, filename):
        self._last_filename = filename
        fp = io.BytesIO()
        self._fp = fp

        if self.lzma:
            fp = lzma.open(fp, 'wb')

        return fp

    def close_fp(self):
        if not self.fp or not self.writer:
            return
        self.writer.write_footer()
        self.fp.close()

        key = Key(self.bucket)
        key.key = self._last_filename
        key.set_contents_from_file(self._fp, cb=self.progress, num_cb=10, rewind=True)
        print()
        self._fp.close()

    def progress(self, done, todo):
        sys.stdout.write('%s %d/%d\r'%(self._last_filename, done, todo))
        sys.stdout.flush()

    def write_last_export(self):
        if not self.last_date:
            return
        
        filename = self.config.get('iaexporter', 'last_export_file')
        open(filename, 'w').write(self.last_date.isoformat())

class IAExporterBootstrap(Bootstrap):
    def start(self):
        super().start()

        self.exporter = IAExporter(self.config)
        self.exporter.dump()

if __name__ == '__main__':
    IAExporterBootstrap().start()
