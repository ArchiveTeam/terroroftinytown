# encoding=utf-8
import argparse
import configparser
import logging

import redis
import tornado.ioloop

from terroroftinytown.tracker.app import Application
from terroroftinytown.tracker.database import Database
from terroroftinytown.tracker.logging import GzipRotatingFileHandler
from terroroftinytown.tracker.stats import Stats


logger = logging.getLogger(__name__)


class Bootstrap:
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser()
        self.config = configparser.ConfigParser()

    def start(self, args=None):
        self.setup_args()
        self.parse_args(args=args)
        self.load_config()
        self.setup_database()

    def setup_args(self):
        self.arg_parser.add_argument('config')
        self.arg_parser.add_argument('--debug', action='store_true')

    def parse_args(self, args=None):
        self.args = self.arg_parser.parse_args(args=args)

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

        self.redis = redis.Redis(**kwargs)

    def setup_stats(self):
        self.stats = Stats(
            self.redis,
            self.config.get('redis', 'prefix', fallback=''),
            self.config.getint('redis', 'max_stats', fallback=30)
        )

    def setup_logging(self):
        log_path = self.config.get('logging', 'path', fallback=None)

        if not log_path:
            return

        if self.args.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        handler = GzipRotatingFileHandler(
            filename=log_path, maxBytes=10485760, backupCount=1000000,
            encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)


class ApplicationBootstrap(Bootstrap):
    def start(self):
        super().start()
        self.setup_redis()
        self.setup_stats()
        self.setup_application()
        self.setup_logging()
        self.boot()

    def setup_application(self):
        self.application = Application(
            self.database,
            self.redis,
            debug=self.args.debug,
            cookie_secret=self.config['web']['cookie_secret'],
        )

    def boot(self):
        logger.info('Application booting. Listen on %s',
                    self.config['web']['port'])
        self.application.listen(int(self.config['web']['port']))
        tornado.ioloop.IOLoop.instance().start()
