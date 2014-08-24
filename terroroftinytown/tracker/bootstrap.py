# encoding=utf-8
import argparse
import configparser
import tornado.ioloop
import redis

from terroroftinytown.tracker.database import Database
from terroroftinytown.tracker.app import Application

class Bootstrap:
    arg_parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()

    def __init__(self):
        self.setup_args()
        self.parse_args()
        self.load_config()
        self.setup_database()

    def setup_args(self):
        self.arg_parser.add_argument('config')
        self.arg_parser.add_argument('--debug', action='store_true')

    def parse_args(self):
        self.args = self.arg_parser.parse_args()

    def load_config(self):
        self.config.read([self.args.config])

    def setup_database(self):
        self.database = Database(
            path=self.config['database']['path'],
        )

    def setup_redis(self):
        kwargs = {
            'db': self.config.getint('redis', 'db', fallback=0),
            'password': self.config.get('redis', 'password', fallback=None),
        }

        if self.config['redis']['unix']:
            kwargs['unix_socket_path'] = self.config['redis']['unix']
        else:
            kwargs['host'] = self.config.get('redis', 'host', fallback='localhost')
            kwargs['port'] = self.config.getint('redis', 'port', fallback=6379)

        self.redis = redis.StrictRedis(**kwargs)

class ApplicationBootstrap(Bootstrap):
    def __init__(self):
        super().__init__()
        self.setup_redis()
        self.setup_application()
        self.boot()

    def setup_application(self):
        self.application = Application(
            self.database,
            self.redis,
            self.config.get('redis', 'prefix', fallback=''),
            debug=self.args.debug,
            cookie_secret=self.config['web']['cookie_secret'],
        )

    def boot(self):
        self.application.listen(int(self.config['web']['port']))
        tornado.ioloop.IOLoop.instance().start()
