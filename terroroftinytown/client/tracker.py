# encoding-utf8
'''Tracker communication.'''
import functools
import json
import logging
import requests
import socket

from terroroftinytown import six
from terroroftinytown.client import VERSION


_logger = logging.getLogger(__name__)


class TrackerError(Exception):
    pass


def reraise_with_tracker_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as error:
            six.reraise(TrackerError, str(error))
    return wrapper


class TrackerClient(object):
    def __init__(self, host, username, version=None, bind_address=None):
        self.host = host
        self.username = username

        self.client_version = version

        if bind_address:
            self.bind_address(bind_address)

    @reraise_with_tracker_error
    def get_item(self):
        _logger.info('Contacting tracker.')

        response = requests.post(
            'http://{host}/api/get'.format(host=self.host),
            data={
                'username': self.username,
                'version': VERSION,
                'client_version': self.client_version,
            },
        )

        response.raise_for_status()
        item = response.json()

        return item

    @reraise_with_tracker_error
    def upload_item(self, claim_id, tamper_key, results):
        _logger.info('Uploading to tracker.')

        response = requests.post(
            'http://{host}/api/done'.format(host=self.host),
            data={
                'claim_id': claim_id,
                'tamper_key': tamper_key,
                'results': json.dumps(results),
            },
        )
        response.raise_for_status()

    def bind_address(self, address):
        '''Set **all, global** socket connections to be outbound from this address'''
        # https://stackoverflow.com/questions/12585317/requests-bind-to-an-ip
        real_create_conn = socket.create_connection

        def set_src_addr(*args):
            address, timeout = args[0], args[1]
            source_address = (address, 0)
            return real_create_conn(address, timeout, source_address)

        socket.create_connection = set_src_addr
