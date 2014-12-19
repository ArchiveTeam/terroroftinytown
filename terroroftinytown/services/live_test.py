'''Test live services.'''
import codecs
import glob
import os
import os.path
import unittest

from terroroftinytown.services.registry import registry
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six import u
import terroroftinytown


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
        'method': 'head',
    },
    'xco': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'url_template': 'http://x.co/{shortcode}',
        'redirect_codes': [301],
        'no_redirect_codes': [200],
        'banned_codes': [403, 420, 429],
        'method': 'head',
    },
    'pub-vitrue-com': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'url_template': 'http://pub.vitrue.com/{shortcode}',
        'redirect_codes': [301],
        'no_redirect_codes': [302],
        'banned_codes': [403, 420, 429],
        'method': 'head',
    },
    'tighturl-com': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'url_template': 'http://tighturl.com/{shortcode}',
        'redirect_codes': [301],
        'no_redirect_codes': [404],
        'banned_codes': [420, 429],
        'method': 'head',
    },
    'tinyurl': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyz',
        'url_template': 'http://tinyurl.com/{shortcode}',
        'redirect_codes': [200, 301, 307],
        'no_redirect_codes': [404],
        'unavailable_codes': [302],
        'banned_codes': [420, 429],
        'method': 'head',
    },
    'adjix': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyz',
        'url_template': 'http://adjix.com/{shortcode}',
        'redirect_codes': [200],
        'no_redirect_codes': [403, 404],
        'unavailable_codes': [],
        'banned_codes': [420, 429],
        'method': 'get',
    },
    'yatuc': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyz',
        'url_template': 'http://yatuc.com/{shortcode}',
        'redirect_codes': [302],
        'no_redirect_codes': [],
        'unavailable_codes': [],
        'banned_codes': [420, 429],
        'method': 'head',
    },
    'shar-es': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'url_template': 'http://shar.es/{shortcode}',
        'redirect_codes': [200, 301],
        'no_redirect_codes': [404],
        'unavailable_codes': [],
        'banned_codes': [403, 420, 429],
        'method': 'get',
        'body_regex': r'<a id="clickthrough"\s+href="([^"]*)">',
    },
    'feedly': {
        'alphabet': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_',
        'url_template': 'http://feedly.com/e/{shortcode}',
        'redirect_codes': [302],
        'no_redirect_codes': [],
        'unavailable_codes': [],
        'banned_codes': [403, 420, 429],
        'method': 'head',
    },
}


class TestLive(unittest.TestCase):
    #  @unittest.skipIf(os.environ.get('NO_LIVE_SERVICE_TEST'), 'no live test')
    def test_custom_services(self):
        # for python 2.6 compatbility
        if os.environ.get('NO_LIVE_SERVICE_TEST'):
            print('SKIP')
            return

        filenames = get_definition_filenames()
        for filename in filenames:
            service_name = os.path.split(filename)[-1].replace('.txt', '')

#             if service_name not in ('tinyurl',):
#                 print('Skip', service_name)
#                 continue

            params = MOCK_PARAMS[service_name]
            service = registry[u(service_name)](params)

            print('Brought up service', service)

            service.prepare()

            with codecs.open(filename, 'rb') as def_file:
                for shortcode, expected_result in iterate_definition_file(def_file):
                    service.current_shortcode = shortcode
                    url = params['url_template'].format(shortcode=shortcode)

                    print('Requesting', url, 'Expect:', expected_result)

                    response = service.fetch_url(url)
                    url_status, result_url, encoding = service.process_response(response)

                    if terroroftinytown.six.PY2 and \
                            isinstance(result_url, terroroftinytown.six.binary_type):
                        result_url = result_url.decode(encoding)

                    print('  Got', url_status, result_url, encoding)

                    if url_status == URLStatus.ok:
                        self.assertEqual(expected_result, result_url)
                    else:
                        self.assertEqual(expected_result, url_status)


def iterate_definition_file(file):
    for line in file:
        line = line.strip()

        if not line or line.startswith(b'#'):
            continue

        if line.startswith(b'?'):
            encoding, line = line[1:].split(b'?', 1)
            encoding = encoding.decode('ascii')

            line = line.decode(encoding)
        else:
            line = line.decode('utf-8')

        shortcode, result = line.split('|', 1)

        yield (shortcode, result)


def get_definition_filenames():
    def_path = os.path.join(os.path.dirname(__file__), 'test-definitions')
    return sorted(glob.glob(def_path + '/*.txt'))
