from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import configparser
import json
import os.path
import requests
import string
import threading
import time
import unittest

import tornado.httpserver
import tornado.testing

from terroroftinytown.tracker.app import Application
from terroroftinytown.tracker.bootstrap import ApplicationBootstrap
from terroroftinytown.tracker.database import Database
from terroroftinytown.tracker.model import MIN_CLIENT_VERSION_OVERRIDE, \
    MIN_VERSION_OVERRIDE
from terroroftinytown.tracker.stats import Stats


class IOLoopThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.io_loop = tornado.ioloop.IOLoop()

    def run(self):
        self.io_loop.start()

    def stop(self):
        self.io_loop.add_callback(self.io_loop.stop)


class TestTracker(unittest.TestCase, ApplicationBootstrap):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        ApplicationBootstrap.__init__(self)

    def parse_args(self, args=None):
        pass

    def load_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'tracker_unittest.conf'
        )

        self.config.read([config_path])

    def setup_database(self):
        print('Set up database')
        self.database = Database(
            path=self.config['database']['path'],
            delete_everything='yes-really!'
        )

    def setup_application(self):
        self.application = Application(self.database, debug=True, cookie_secret='TEST')

    def boot(self):
        self.io_loop_thread = IOLoopThread()
        socket_obj, self.port = tornado.testing.bind_unused_port()
        http_server = tornado.httpserver.HTTPServer(
            self.application, io_loop=self.io_loop_thread.io_loop
        )
        http_server.add_socket(socket_obj)
        self.io_loop_thread.start()

    def setUp(self):
        self.start()
        Stats.instance.clear()
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.io_loop_thread.stop()
        self.driver.close()

    def get_url(self, path):
        return 'http://localhost:{0}{1}'.format(self.port, path)

    def sleep(self, seconds=0.5):
        time.sleep(seconds)

    def test_all(self):
        self.sign_in()
        self.sleep()
        self.sign_out()
        self.sleep()
        self.sign_in_bad()
        self.sleep()
        self.sign_in()
        self.sleep()
        self.create_user()
        self.sleep()
        self.sign_out()
        self.sleep()
        self.sign_in_second_user()
        self.sleep()
        self.sign_out()
        self.sleep()
        self.sign_in()
        self.sleep()
        self.create_project()
        self.sleep()
        self.config_project_settings()
        self.sleep()
        self.populate_queue()
        self.sleep()
        self.get_project_settings()
        self.sleep()
        self.claim_with_outdated_script()
        self.sleep()
        self.claim_and_return_an_item()
        self.sleep()
        # these tests are run after an item have been submitted
        self.global_stats()
        self.sleep()
        self.live_stats()
        self.sleep()
        self.live_stats_update()

    def global_stats(self):
        self.driver.get(self.get_url('/'))
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ng-binding'))
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("globalstats")//strong[1]').text,
            '20'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("globalstats")//strong[2]').text,
            '1'
        )

    def live_stats(self):
        self.driver.get(self.get_url('/'))
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ng-binding'))
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-recent")//tbody/tr[1]/td[1]').text,
            'SMAUG'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-recent")//tbody/tr[1]/td[2]').text,
            '1'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-recent")//tbody/tr[1]/td[3]').text,
            '20'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-recent")//tbody/tr[1]/td[4]').text,
            'test_project'
        )

    def live_stats_update(self):
        self.driver.get(self.get_url('/'))
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ng-binding'))
        )
        self.claim_and_return_an_item()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, 'id("leaderboard-recent")//tbody/tr[2]'))
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-recent")//tbody/tr[1]/td[3]').text,
            '20'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-totals")//tbody/tr[1]/td[2]').text,
            '2'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("leaderboard-totals")//tbody/tr[1]/td[3]').text,
            '40'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("globalstats")//strong[1]').text,
            '40'
        )
        self.assertEqual(
            self.driver.find_element_by_xpath('id("globalstats")//strong[2]').text,
            '2'
        )

    def sign_in(self):
        self.driver.get(self.get_url('/'))

        element = self.driver.find_element_by_link_text('Tracker admin')

        element.click()

        element = self.driver.find_element_by_name('username')
        element.send_keys('test_user')

        element = self.driver.find_element_by_name('password')
        element.send_keys('test_password')

        element.submit()

        WebDriverWait(self.driver, 10).until(
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

        WebDriverWait(self.driver, 20).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, 'body'), 'Log in failed'
            )
        )

    def sign_out(self):
        element = self.driver.find_element_by_link_text('Log out')
        element.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('URLTeam Tracker')
        )

    def create_user(self):
        element = self.driver.find_element_by_link_text('Users')
        element.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('Users')
        )

        element = self.driver.find_element_by_name('username')
        element.send_keys('user2')

        element = self.driver.find_element_by_name('password')
        element.send_keys('userpass1')

        element.submit()

        element = self.driver.find_element_by_link_text('Users')
        element.click()

        WebDriverWait(self.driver, 10).until(
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

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('Overview')
        )

    def create_project(self):
        element = self.driver.find_element_by_link_text('Projects')
        element.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('Projects')
        )

        element = self.driver.find_element_by_name('name')
        element.send_keys('test_project')

        element.submit()

    def config_project_settings(self):
        self.driver.get(self.get_url('/admin/'))

        element = self.driver.find_element_by_link_text('Projects')
        element.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('Projects')
        )

        element = self.driver.find_element_by_link_text('test_project')
        element.click()

        element = self.driver.find_element_by_link_text('Shortener Settings')
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

    def populate_queue(self):
        element = self.driver.find_element_by_link_text('Claims')
        element.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.title_is('Items')
        )

        element = self.driver.find_element_by_name('items')
        element.send_keys('0-19\n20-39')

        element.submit()

    def get_project_settings(self):
        response = requests.get(
            self.get_url('/api/project_settings?name=test_project'),
        )

        print(response.reason)
        self.assertEqual(200, response.status_code)

        settings = response.json()

        self.assertEqual('test_project', settings['name'])

    def claim_with_outdated_script(self):
        response = requests.post(
            self.get_url('/api/get'),
            data={
                'username': 'SMAUG',
                'version':-1,
                'client_version':-1,
            }
        )
        print(response.reason)
        self.assertEqual(412, response.status_code)

    def claim_and_return_an_item(self):
        response = requests.post(
            self.get_url('/api/get'),
            data={
                'username': 'SMAUG',
                'version': MIN_VERSION_OVERRIDE,
                'client_version': MIN_CLIENT_VERSION_OVERRIDE
            }
        )
        print(response.reason)
        self.assertEqual(200, response.status_code)
        item = response.json()

        print(item)

        item['project']

        response = requests.post(
            self.get_url('/api/done'),
            data={
                'claim_id': item['id'],
                'tamper_key': item['tamper_key'],
                'results': json.dumps({
                    'abcd': {
                        'url': 'http://ultraarchive.org',
                        'encoding': 'ascii',
                    }
                })
            }
        )

        print(response.reason)
        self.assertEqual(200, response.status_code)

        doc = response.json()

        print(doc)
