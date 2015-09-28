# encoding=utf-8
import itertools
import logging
import time

from terroroftinytown.client.errors import PleaseRetry, ScraperError,\
    MalformedResponse
from terroroftinytown.services.registry import registry
from terroroftinytown.six import u


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

    MAX_RETRY_COUNT = 10

    def __init__(self, shortener_params, todo_list, max_try_count=MAX_RETRY_COUNT):
        self.params = shortener_params
        self.todo_list = todo_list
        self.max_try_count = max_try_count
        self.results = {}
        self.service = self.get_service()(self.params)

    def run(self):
        self.service.prepare()

        for item in self.todo_list:
            for try_count in itertools.count():
                if try_count > 0:
                    _logger.info('Attempt %d', (try_count + 1))

                if try_count > self.max_try_count:
                    if hasattr(self.service, 'current_shortcode'):
                        shortcode = self.service.current_shortcode
                    else:
                        shortcode = ''

                    raise ScraperError(
                        'Number of attempts exceeded for {0} ({1}).'
                        .format(repr(item), shortcode)
                    )

                try:
                    result = self.service.scrape_one(item)
                except PleaseRetry:
                    time.sleep(10 * try_count)
                except MalformedResponse:
                    _logger.info('Skipped URL due to malformed response.')
                else:
                    if result:
                        self.results[result['shortcode']] = result

                    self.service.wait()

                    break

        return self.results

    def get_service(self):
        if self.params['name'] in registry:
            return registry[self.params['name']]
        else:
            return registry[u('_default')]
