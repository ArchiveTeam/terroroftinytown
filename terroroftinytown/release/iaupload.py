import logging

import internetarchive

from terroroftinytown.release.baseuploader import BaseUploaderBootstrap


logger = logging.getLogger(__name__)


class IAUploaderBootstrap(BaseUploaderBootstrap):
    def upload(self):
        item = internetarchive.get_item(self.identifier)
        metadata = dict(
            title=self.title,
            collection=self.collection,
            mediatype='software',
            subject=self.subject,
            description=self.description,
        )

        logger.info('Begin upload %s %s.', self.identifier, self.filenames)

        item.upload(self.filenames, metadata=metadata,
                    verify=True, verbose=True,
                    access_key=self.access_key, secret_key=self.secret_key,
                    retries=10)

        logger.info('Done upload.')


if __name__ == '__main__':
    bootstrap = IAUploaderBootstrap()
    bootstrap.start()
