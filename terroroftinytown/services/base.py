# encoding=utf-8
'''Base class for URL shortener services'''

import datetime
import logging
import re
import time

from requests.exceptions import ConnectionError

from terroroftinytown.client import alphabet, VERSION
from terroroftinytown.client.errors import (UnhandledStatusCode,
    UnexpectedNoResult, ScraperError, PleaseRetry)
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six import u


__all__ = ['BaseService', 'registry']
DEFAULT_USER_AGENT = 'ArchiveTeam TerrorOfTinyTown/{0} ({1})'.format(
    VERSION, datetime.datetime.utcnow())


class BaseService(object):
    def __init__(self, params):
        self.params = params
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_shortcode = None
        self.user_agent = DEFAULT_USER_AGENT

    def wait(self):
        sleep_time = self.params['request_delay']
        time.sleep(sleep_time)

    def transform_sequence_num(self, sequence_number):
        return alphabet.int_to_str(
            sequence_number, self.params['alphabet']
        )

    def scrape_one(self, sequence_number):
        self.current_shortcode = shortcode = self.transform_sequence_num(sequence_number)
        url = self.params['url_template'].format(shortcode=shortcode)

        self.logger.info('Requesting %s', url)

        response = self.fetch_url(url)
        url_status, result_url, encoding = self.process_response(response)

        if url_status == URLStatus.ok:
            assert result_url is not None
            self.logger.info('Got a result.')
            self.logger.debug('%s %s', result_url, response.encoding)

            return {
                'shortcode': shortcode,
                'url': result_url,
                'encoding': encoding or 'latin-1'
            }

    def fetch_url(self, url):
        # this import is moved here so that tracker can import
        # registry without installing requests
        import requests
        headers = {
            'User-Agent': self.user_agent,
        }

        try:
            if self.params['method'] == 'get':
                response = requests.get(
                    url, allow_redirects=False, headers=headers)
            else:
                response = requests.head(
                    url, allow_redirects=False, headers=headers)
        except ConnectionError as e:
            return self.process_connection_error(e)

        return response

    def process_response(self, response):
        status_code = response.status_code

        if status_code in self.params['redirect_codes']:
            return self.process_redirect(response)
        elif status_code in self.params['no_redirect_codes']:
            return self.process_no_redirect(response)
        elif status_code in self.params['unavailable_codes']:
            return self.process_unavailable(response)
        elif status_code in self.params['banned_codes']:
            return self.process_banned(response)
        else:
            return self.process_unknown_code(response)

    def process_redirect(self, response):
        if 'Location' in response.headers:
            result_url = response.headers['Location']
            return (URLStatus.ok, result_url, None)
        elif self.params.get('body_regex'):
            return self.process_redirect_body(response)
        else:
            raise UnexpectedNoResult()

    def process_redirect_body(self, response):
        pattern = self.params['body_regex']
        match = re.search(pattern, response.text)

        if match:
            return (URLStatus.ok, match.group(1), response.encoding)
        else:
            raise UnexpectedNoResult()

    def process_no_redirect(self, response):
        return (URLStatus.not_found, None, None)

    def process_unavailable(self, response):
        return (URLStatus.unavailable, None, None)

    def process_banned(self, response):
        raise PleaseRetry('Server said: {0}'.format(repr(response.reason)))

    def process_unknown_code(self, response):
        raise UnhandledStatusCode(
            'Unknown status code {0}'.format(response.status_code)
        )

    def process_connection_error(self, exception):
        raise PleaseRetry('Connection error: {0}'.format(repr(exception.args)))


class DefaultService(BaseService):
    pass
