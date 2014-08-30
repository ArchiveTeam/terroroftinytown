# encoding=utf-8
'''Base class for URL shortener services'''

import logging
import re
import requests
import time

from terroroftinytown.client import alphabet
from terroroftinytown.client.errors import (UnhandledStatusCode,
    UnexpectedNoResult, ScraperError, PleaseRetry)

__all__ = ['BaseService', 'registry']

registry = {}

class BaseService:
    def __init__(self, params):
        self.params = params
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_shortcode = None

    def wait(self):
        sleep_time = self.params['request_delay']
        time.sleep(sleep_time)

    def scrape_one(self, sequence_number):
        self.current_shortcode = shortcode = alphabet.int_to_str(
            sequence_number, self.params['alphabet']
        )
        url = self.params['url_template'].format(shortcode=shortcode)

        self.logger.info('Requesting %s', url)

        response = self.fetch_url(url)
        result_url = self.process_response(response)

        if result_url is not None:
            self.logger.info('Got a result.')
            self.logger.debug('%s %s', result_url, response.encoding)

            return {
                'shortcode': shortcode,
                'url': result_url,
                'encoding': response.encoding or 'latin-1'
            }

    def fetch_url(self, url):
        if self.params['method'] == 'get':
            response = requests.get(url, allow_redirects=False)
        else:
            response = requests.head(url, allow_redirects=False)

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
            return result_url
        else:
            return self.process_redirect_body(response)

    def process_redirect_body(self, response):
        pattern = self.params['body_regex']
        match = re.search(pattern, response.text)

        if match:
            return match.group(1)
        else:
            raise UnexpectedNoResult()

    def process_no_redirect(self, response):
        return None

    def process_unavailable(self, response):
        raise ScraperError('Not implemented.')

    def process_banned(self, response):
        raise PleaseRetry()

    def process_unknown_code(self, response):
        raise UnhandledStatusCode(
            'Unknown status code {0}'.format(response.status_code)
        )

registry['_default'] = BaseService
