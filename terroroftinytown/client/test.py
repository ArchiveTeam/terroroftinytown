# encoding=utf-8
import threading
import unittest

import tornado.ioloop
import tornado.testing
import tornado.web

from terroroftinytown.client.scraper import Scraper
from terroroftinytown.client.errors import ScraperError


class ExampleApp(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self,
            [
                (r'/([a-zA-Z0-9]+)', ExampleHandler)
            ],
            debug=True)


class ExampleHandler(tornado.web.RequestHandler):
    def get(self, shortcode):
        if shortcode == 'a':
            self.redirect('http://archive.land', status=301)
        elif shortcode == 'b':
            self.write(b'<html><body>Please watch this ad.')
            self.write(b'<img><a id="contlink" href="http://yahoo.city">.')
            self.write(b'continue</a></html><body>')
        elif shortcode == 'd':
            self.set_status(420, 'banned')
        else:
            self.redirect('http://example.com', status=303)

    def head(self, shortcode):
        self.get(shortcode)


class IOLoopThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.io_loop = tornado.ioloop.IOLoop()

    def run(self):
        self.io_loop.start()

    def stop(self):
        self.io_loop.add_callback(self.io_loop.stop)


class TestTracker(unittest.TestCase):
    def setUp(self):
        self.io_loop_thread = IOLoopThread()
        app = ExampleApp()
        socket_obj, self.port = tornado.testing.bind_unused_port()
        http_server = tornado.httpserver.HTTPServer(
            app, io_loop=self.io_loop_thread.io_loop
        )
        http_server.add_socket(socket_obj)

        self.io_loop_thread.start()

    def tearDown(self):
        self.io_loop_thread.stop()

    def get_url(self, path):
        return 'http://localhost:{0}{1}'.format(self.port, path)

    def test_scraper(self):
        scraper = Scraper(
            {
                'alphabet': 'abcdefghijklmnopqrstuvwxyz',
                'url_template': self.get_url('/{shortcode}'),
                'request_delay': 0.1,
                'redirect_codes': [301, 200],
                'no_redirect_codes': [303],
                'unavailable_codes': [],
                'banned_codes': [420],
                'body_regex': r'id="contlink" href="([^"]+)',
                'custom_code_required': False,
                'method': 'get',
                'name': 'blah',
            },
            [0, 1, 2]
        )

        scraper.run()

        self.assertEqual(2, len(scraper.results))
        self.assertEqual('http://archive.land', scraper.results['a']['url'])
        self.assertEqual('http://yahoo.city', scraper.results['b']['url'])

    def test_scraper_banned(self):
        scraper = Scraper(
            {
                'alphabet': 'abcdefghijklmnopqrstuvwxyz',
                'url_template': self.get_url('/{shortcode}'),
                'request_delay': 0.1,
                'redirect_codes': [301, 200],
                'no_redirect_codes': [303],
                'unavailable_codes': [],
                'banned_codes': [420],
                'body_regex': r'id="contlink" href="([^"]+)',
                'custom_code_required': False,
                'method': 'get',
                'name': 'blah',
            },
            [3],
            max_try_count=1
        )

        try:
            scraper.run()
        except ScraperError:
            pass
        else:
            self.fail()
