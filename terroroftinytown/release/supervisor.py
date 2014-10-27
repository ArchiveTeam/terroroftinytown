import argparse
import json
import logging
import os.path
import sys
import time

from terroroftinytown.release.iaupload import IAUploaderBootstrap
from terroroftinytown.tracker.export import ExporterBootstrap
from terroroftinytown.tracker.bootstrap import Bootstrap


ROOT_PATH = os.environ.get('ROOT_PATH', '/home/tinytown/tinytown-export/')
SENTINEL_FILE = os.path.join(ROOT_PATH, 'tinytown-supervisor-sentinel')

logger = logging.getLogger(__name__)


def main():
    log_filename = os.path.join(ROOT_PATH, 'supervisor.log')
    logging.basicConfig(level=logging.INFO, filename=log_filename)
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

    bootstrap = Bootstrap()
    bootstrap.parse_args(args=[config_path])
    bootstrap.load_config()

    time_struct = time.gmtime()
    timestamp = bootstrap.config.get(
        'iaexporter', 'timestamp',
        vars=dict(
            year=time_struct.tm_year,
            month=time_struct.tm_mon,
            day=time_struct.tm_mday,
            hour=time_struct.tm_hour,
            minute=time_struct.tm_min,
            second=time_struct.tm_sec,
        )
    )

    export_directory = os.path.join(ROOT_PATH, timestamp)

    logger.info('Begin export to %s.', export_directory)

    title = bootstrap.config.get(
        'iaexporter', 'title', vars=dict(timestamp=timestamp)
    )
    identifier = bootstrap.config.get(
        'iaexporter', 'item', vars=dict(timestamp=timestamp)
    )

    upload_meta_path = os.path.join(ROOT_PATH, 'current.json')
    upload_meta = {
        'identifier': identifier,
        'title': title
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

    export_dir_start_size = get_dir_size(export_directory)

    exporter.start(args=args)

    logger.info('Export finished')

    export_dir_end_size = get_dir_size(export_directory)

    if export_dir_start_size == export_dir_end_size:
        raise Exception('Export directory size did not change: {} bytes'
                        .format(export_dir_end_size))

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


def get_dir_size(path):
    total = 0

    for root, dirs, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(root, name))
                     for name in files)

    return total


if __name__ == '__main__':
    main()
