# encoding=utf-8
import argparse
import configparser
import tornado.ioloop

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

class ApplicationBootstrap(Bootstrap):
    def __init__(self):
        super().__init__()
        self.setup_application()
        self.boot()

    def setup_application(self):
        self.application = Application(
            self.database,
            debug=self.args.debug,
            cookie_secret=self.config['web']['cookie_secret'],
        )

    def boot(self):
        self.application.listen(int(self.config['web']['port']))
        tornado.ioloop.IOLoop.instance().start()
