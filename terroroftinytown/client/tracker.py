# encoding-utf8
'''Tracker communication.'''
import logging
import requests


_logger = logging.getLogger(__name__)


class TrackerError(Exception):
    pass


class TrackerClient(object):
    def __init__(self, host, username, bind_address=None, version=None):
        self.host = host
        self.username = username
        self.bind_address = bind_address
        self.version = version

    def get_item(self):
        _logger.info('Contacting tracker.')

        response = requests.post(
            'http://{host}/api/get',
            data={
                'username': self.username,
                'ip_address': self.bind_address,
                'version': self.version,
            },
        )

        response.raise_for_status()
        item = response.json()

        return item

    def upload_item(self, claim_id, tamper_key, results):
        _logger.info('Uploading to tracker.')

        response = requests.post(
            'http://{host}/api/done',
            data={
                'claim_id': claim_id,
                'tamper_key': tamper_key,
                'results': results,
            },
        )
        response.raise_for_status()
