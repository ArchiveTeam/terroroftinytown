# encoding: utf-8

import logging
import os.path
import sys

from boto.exception import S3CreateError
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
import boto

from terroroftinytown.release.baseuploader import BaseUploaderBootstrap


logger = logging.getLogger(__name__)


class BotoUploaderBootstrap(BaseUploaderBootstrap):
    def upload(self):
        self.setup_boto()

        logger.info('Begin upload %s %s.', self.identifier, self.filenames)

        for filename in self.filenames:
            key = Key(self.bucket)
            key.key = os.path.basename(filename)

            def progress(done, todo):
                sys.stdout.write('%s %d/%d\r' % (filename, done, todo))
                sys.stdout.flush()

            key.set_contents_from_filename(filename, cb=progress)

        logger.info('Done upload.')

    def setup_boto(self):
        self.boto = boto.connect_s3(
            self.access_key,
            self.secret_key,
            host=self.config.get('iaexporter', 'endpoint'),
            is_secure=False,
            calling_format=OrdinaryCallingFormat()
        )
        bucket_name = self.identifier
        try:
            self.bucket = self.boto.create_bucket(bucket_name, {
                'x-archive-meta-title': self.title,
                'x-archive-meta-collection': self.collection,
                'x-archive-meta-mediatype': 'software',
                'x-archive-meta-subject': 'urlteam;terroroftinytown',
                'x-archive-meta-description': self.description,
                'x-archive-ignore-preexisting-bucket': '1'
            })
        except S3CreateError:
            self.bucket = self.boto.get_bucket(bucket_name)


if __name__ == '__main__':
    BotoUploaderBootstrap().start()
