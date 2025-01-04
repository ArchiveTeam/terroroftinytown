import logging

import internetarchive

from terroroftinytown.release.baseuploader import BaseUploaderBootstrap


logger = logging.getLogger(__name__)

RETRY_SLEEP_TIME = 3600 # 1 hour


class IAUploaderBootstrap(BaseUploaderBootstrap):
    def upload(self):
        config = {
            's3': {
                'access': self.access_key,
                'secret': self.secret_key,
            }
        }
        session = internetarchive.get_session(config=config)
        item = session.get_item(self.identifier)

        metadata = dict(
            title=self.title,
            collection=self.collection,
            mediatype=self.mediatype,
            subject=self.subject,
            description=self.description,
        )

        logger.info('Begin upload %s %s.', self.identifier, self.filenames)

        item.upload(self.filenames, metadata=metadata,
                    verify=True, verbose=True,
                    retries=50, retries_sleep=RETRY_SLEEP_TIME)

        logger.info('Done upload.')


if __name__ == '__main__':
    bootstrap = IAUploaderBootstrap()
    bootstrap.start()
