'''Test live services.'''
import glob
import os.path

from terroroftinytown import services
from terroroftinytown.services.status import URLStatus
from terroroftinytown.tracker.model import Project
import unittest


MOCK_PARAMS = {
    'isgd': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
        'url_template': 'http://is.gd/{shortcode}',
        'redirect_codes': [301, 302],
        'no_redirect_codes': [404],
        'unavailable_codes': [200, 410],
        'banned_codes': [403, 420, 429, 502],
        'method': 'get',
    }
}


class TestLive(unittest.TestCase):
    def test_custom_services(self):
        filenames = get_definition_filenames()
        for filename in filenames:
            service_name = os.path.split(filename)[-1].replace('.txt', '')
            params = MOCK_PARAMS[service_name]
            service = services.registry[service_name](params)

            print('Brought up service', service)

            with open(filename) as def_file:
                for shortcode, expected_result in iterate_defintiion_file(def_file):
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


def iterate_defintiion_file(file):
    for line in file:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        shortcode, result = line.split('|', 1)

        yield (shortcode, result)


def get_definition_filenames():
    def_path = os.path.join(os.path.dirname(__file__), 'test-definitions')
    return glob.glob(def_path + '/*.txt')
