# encoding=utf-8
import argparse
import configparser
import tornado.ioloop

from terroroftinytown.tracker.app import Application
from terroroftinytown.tracker.database import Database


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config')
    arg_parser.add_argument('--debug', action='store_true')
    args = arg_parser.parse_args()

    config_parser = configparser.ConfigParser()
    config_parser.read([args.config])

    database = Database(
        path=config_parser['database']['path'],
    )

    application = Application(
        database,
        debug=args.debug,
        cookie_secret=config_parser['web']['cookie_secret'],
    )

    application.listen(int(config_parser['web']['port']))
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
