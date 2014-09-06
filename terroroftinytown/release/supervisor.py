import argparse
import json
import logging
import os.path
import sys
import time

from terroroftinytown.release.iaupload import IAUploaderBootstrap
from terroroftinytown.tracker.export import ExporterBootstrap


ROOT_PATH = '/home/urlteam/tinytown/data/'
SENTINEL_FILE = os.path.join(ROOT_PATH, 'tinytown-supervisor-sentinel')

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    arg_parser = argparse.ArgumentParser('config_path')
    args = arg_parser.parse_args()

    logger.info('Supervisor starting up.')

    try:
        wrapper(args.config_path)
    except Exception:
        logger.exception()
        raise

    logger.info('Supervisor done.')


def wrapper(config_path):
    if os.path.exists(SENTINEL_FILE):
        raise Exception(
            'The sentinel file exists. '
            'Previous supervisor did not exit correctly.'
            )
    else:
        with open(SENTINEL_FILE, 'wb'):
            pass

    if not sys.version_info[0] != 3:
        raise Exception('This script expects Python 3')

    if not os.path.isfile(config_path):
        raise Exception('Config path is not a file.')

    # FIXME: the templates could be a config file option maybe
    timestamp = '{:04}{:02}{:02}T{:02}{:02}{:02}'.format(*time.gmtime())
    export_directory = os.path.join(ROOT_PATH, timestamp)

    logger.info('Begin export to %s.', export_directory)

    upload_meta_path = os.path.join(ROOT_PATH, 'current.json')
    upload_meta = {
        'identifier': 'urlteam_{}'.format(timestamp),
        'title': 'URLTeam Release {}'.format(timestamp)
    }

    with open(upload_meta_path, 'w') as out_file:
        out_file.write(json.dumps(upload_meta))

    os.makedirs(export_directory)

    exporter = ExporterBootstrap()
    args = [
        config_path, '--format', 'beacon',
        '--include-settings', '--zip',
        '--dir-length', '0', '--file-length', '0', '--max-right', '8',
        '--delete',
        export_directory,
        ]
    exporter.start(args=args)

    logger.info('Export finished')

    # TODO: check if the export actually exported anything


    logger.info('Upload starting')

    uploader = IAUploaderBootstrap()
    args = [
        export_directory,
        '--title', upload_meta['title'],
        '--identifier', upload_meta['identifier']
    ]
    uploader.start(args=args)

    logger.info('Upload done.')

    os.remove(SENTINEL_FILE)

    logger.info('Done')


if __name__ == '__main__':
    main()
