'''Test live services.'''
import codecs
import glob
import os.path
import unittest

from terroroftinytown.services.status import URLStatus
from terroroftinytown.six import u
from terroroftinytown.services.registry import registry


MOCK_PARAMS = {
    'isgd': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
        'url_template': 'http://is.gd/{shortcode}',
        'redirect_codes': [301, 302],
        'no_redirect_codes': [404],
        'unavailable_codes': [200, 410],
        'banned_codes': [403, 420, 429, 502],
        'method': 'get',
    },
    'bitly': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_',
        'url_template': 'http://bit.ly/{shortcode}',
        'redirect_codes': [301, 302],
        'no_redirect_codes': [404],
        'unavailable_codes': [410],
        'banned_codes': [403],
        'method': 'heat',
    },
}


class TestLive(unittest.TestCase):
    def test_custom_services(self):
        filenames = get_definition_filenames()
        for filename in filenames:
            service_name = os.path.split(filename)[-1].replace('.txt', '')
            params = MOCK_PARAMS[service_name]
            service = registry[u(service_name)](params)

            print('Brought up service', service)

            with codecs.open(filename, 'r', encoding='utf-8') as def_file:
                for shortcode, expected_result in iterate_definition_file(def_file):
                    service.current_shortcode = shortcode
                    url = params['url_template'].format(shortcode=shortcode)

                    print('Requesting', url, 'Expect:', expected_result)

                    response = service.fetch_url(url)
                    url_status, result_url = service.process_response(response)

                    print('  Got', url_status, result_url)

                    if url_status == URLStatus.ok:
                        self.assertEqual(expected_result, result_url)
                    else:
                        self.assertEqual(expected_result, url_status)


def iterate_definition_file(file):
    for line in file:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        shortcode, result = line.split('|', 1)

        yield (shortcode, result)


def get_definition_filenames():
    def_path = os.path.join(os.path.dirname(__file__), 'test-definitions')
    return sorted(glob.glob(def_path + '/*.txt'))
