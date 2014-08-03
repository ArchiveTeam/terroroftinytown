# encoding=utf-8
import logging
import re
import requests
import time

from terroroftinytown.client import alphabet
from terroroftinytown.client.errors import (UnhandledStatusCode,
    UnexpectedNoResult, ScraperError, PleaseRetry)


_logger = logging.getLogger(__name__)


class Scraper(object):
    '''URL shortner scraper.

    Args:
        shortener_params (dict): The mapping has the keys:

            * url_template (str)
            * alphabet (str)
            * redirect_codes (list)
            * no_redirect_codes (list)
            * unavailable_codes (list)
            * banned_codes (list)

        todo_list (list): A list of integers.

    '''

    def __init__(self, shortener_params, todo_list):
        self.params = shortener_params
        self.todo_list = todo_list
        self.current_shortcode = None
        self.results = {}

    def run(self):
        while self.todo_list:
            self.scrape_one()
            sleep_time = self.params['request_delay']
            time.sleep(sleep_time)

        return self.results

    def scrape_one(self):
        sequence_number = self.todo_list.pop()
        self.current_shortcode = shortcode = alphabet.int_to_str(
            sequence_number, self.params['alphabet']
        )
        url = self.params['url_template'].format(shortcode=shortcode)

        _logger.info('Requesting %s', url)

        response = self.fetch_url(url)
        result_url = self.process_response(response)

        if result_url is not None:
            _logger.info('Got a result.')
            _logger.debug('%s %s', result_url, response.encoding)

            self.results[shortcode] = {
                'url': result_url,
                'encoding': response.encoding
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
