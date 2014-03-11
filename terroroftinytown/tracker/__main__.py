# encoding=utf-8
import argparse
import tornado.ioloop

from terroroftinytown.tracker.app import Application
from terroroftinytown.tracker.database import Database


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--port', default=8888, type=int)
    arg_parser.add_argument('--debug', action='store_true')
    args = arg_parser.parse_args()

    database = Database()

    application = Application(
        database,
        debug=args.debug,
        cookie_secret='asdf',
    )

    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
