import configparser
import os.path
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import threading
import tornado.httpserver
import tornado.testing
import unittest

from terroroftinytown.tracker.app import Application
from terroroftinytown.tracker.database import Database
from selenium.webdriver.common.by import By
import string
import requests


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
        config_parser = configparser.ConfigParser()
        config_path = os.path.join(
            os.path.dirname(__file__),
            'tracker_unittest.conf'
        )

        config_parser.read([config_path])

        database = Database(
            host=config_parser['redis']['host'],
            port=int(config_parser['redis']['port']),
            db=int(config_parser['redis']['database']),
        )

        database.connection.flushdb()

        self.io_loop_thread = IOLoopThread()
        app = Application(database, debug=True, cookie_secret='TEST')
        socket_obj, self.port = tornado.testing.bind_unused_port()
        http_server = tornado.httpserver.HTTPServer(
            app, io_loop=self.io_loop_thread.io_loop
        )
        http_server.add_socket(socket_obj)

        self.driver = webdriver.Firefox()

        self.io_loop_thread.start()

    def tearDown(self):
        self.io_loop_thread.stop()
        self.driver.close()

    def get_url(self, path):
        return 'http://localhost:{0}{1}'.format(self.port, path)

    def test_all(self):
        self.sign_in()
        self.sign_out()
        self.sign_in_bad()
        self.sign_in()
        self.create_user()
        self.sign_out()
        self.sign_in_second_user()
        self.sign_out()
        self.sign_in()
        self.create_project()
        self.config_project_settings()
        self.claim_and_return_an_item()

    def sign_in(self):
        self.driver.get(self.get_url('/'))

        element = self.driver.find_element_by_link_text('Tracker admin')

        element.click()

        element = self.driver.find_element_by_name('username')
        element.send_keys('test_user')

        element = self.driver.find_element_by_name('password')
        element.send_keys('test_password')

        element.submit()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('Overview')
        )

    def sign_in_bad(self):
        self.driver.get(self.get_url('/'))

        element = self.driver.find_element_by_link_text('Tracker admin')

        element.click()

        element = self.driver.find_element_by_name('username')
        element.send_keys('test_user')

        element = self.driver.find_element_by_name('password')
        element.send_keys('badpass')

        element.submit()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, 'body'), 'Log in failed'
            )
        )

    def sign_out(self):
        element = self.driver.find_element_by_link_text('Log out')
        element.click()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('URLTeam Tracker')
        )

    def create_user(self):
        element = self.driver.find_element_by_link_text('Users')
        element.click()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('Users')
        )

        element = self.driver.find_element_by_name('username')
        element.send_keys('user2')

        element = self.driver.find_element_by_name('password')
        element.send_keys('userpass1')

        element.submit()

        element = self.driver.find_element_by_link_text('Users')
        element.click()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, 'body'), 'user2'
            )
        )

    def sign_in_second_user(self):
        self.driver.get(self.get_url('/'))

        element = self.driver.find_element_by_link_text('Tracker admin')

        element.click()

        element = self.driver.find_element_by_name('username')
        element.send_keys('user2')

        element = self.driver.find_element_by_name('password')
        element.send_keys('userpass1')

        element.submit()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('Overview')
        )

    def create_project(self):
        element = self.driver.find_element_by_link_text('Projects')
        element.click()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('Projects')
        )

        element = self.driver.find_element_by_name('name')
        element.send_keys('test_project')

        element.submit()

    def config_project_settings(self):
        self.driver.get(self.get_url('/admin/'))

        element = self.driver.find_element_by_link_text('Projects')
        element.click()

        WebDriverWait(self.driver, 2).until(
            expected_conditions.title_is('Projects')
        )

        element = self.driver.find_element_by_link_text('test_project')
        element.click()

        element = self.driver.find_element_by_link_text('Settings')
        element.click()

        element = self.driver.find_element_by_name('alphabet')
        element.clear()
        element.send_keys(string.ascii_lowercase)
        element.send_keys(string.ascii_uppercase)
        element.send_keys(string.digits)

        element = self.driver.find_element_by_name('url_template')
        element.clear()
        element.send_keys('http://www.example.com/{shortcode}')

        element = self.driver.find_element_by_name('request_delay')
        element.clear()
        element.send_keys('1.0')

        element = self.driver.find_element_by_name('redirect_codes')
        element.clear()
        element.send_keys('301 302')

        element = self.driver.find_element_by_name('no_redirect_codes')
        element.clear()
        element.send_keys('404')

        element = self.driver.find_element_by_name('unavailable_codes')
        element.clear()
        element.send_keys('200')

        element = self.driver.find_element_by_name('banned_codes')
        element.clear()
        element.send_keys('420')

        element = self.driver.find_element_by_name('body_regex')
        element.clear()
        element.send_keys('<a id="redir_link" href="[^"]+">')

        element.submit()

    def claim_and_return_an_item(self):
        response = requests.post(
            self.get_url('/api/get'),
            payload={'username': 'SMAUG'}
        )
        self.assertEqual(200, response.status_code)
        item = response.json()

        item['shortener_params']

        response = requests.post(
            self.get_url('/api/done'),
            params={
                'claim_id': item['claim_id'],
                'tamper_key': item['tamper_key'],
                'results': {
                    'abcd': {
                        'url': 'http://ultraarchive.org',
                        'encoding': 'ascii',
                    }
                }
            }
        )

        self.assertEqual(200, response.status_code)
