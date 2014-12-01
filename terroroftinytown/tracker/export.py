# encoding=utf-8

import base64
import collections
import itertools
import logging
import os, lzma
import pickle
import shutil
import zipfile

from sqlalchemy import func
from sqlalchemy.sql.expression import delete

from terroroftinytown.format import registry
from terroroftinytown.format.projectsettings import ProjectSettingsWriter
from terroroftinytown.format.urlformat import quote
from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.model import new_session, Project, Result
from terroroftinytown.util.externalsort import GNUExternalSort


logger = logging.getLogger(__name__)


ResultContainer = collections.namedtuple(
    'ResultContainer',
    ['id', 'shortcode', 'url', 'encoding', 'datetime']
)


class Exporter:
    def __init__(self, output_dir, format="beacon", settings={}):
        super().__init__()

        self.setup_format(format)
        self.output_dir = output_dir
        self.settings = settings
        self.after = self.settings['after']
        self.max_items = self.settings['max_items']

        self.projects_count = 0
        self.items_count = 0
        self.last_date = None

        self.lzma = True
        self.extension = 'txt.xz'

        # Length of directory name
        self.dir_length = settings['dir_length']
        # Number of characters from the right are not used in directory name
        # in other words, number of _
        self.max_right = settings['max_right']
        # Number of characters from the left that are used in file name
        # in other words, number of characters that are not in directory name and not _
        self.file_length = settings['file_length']

        # Example of settings:
        # dir_length = 2
        # max_right = 4
        # file_length = 2
        # output: projectname/00/01/000100____.txt, projectname/01/01__.txt

        self.fp = None
        self.writer = None
        self.project_result_sorters = {}

        self.working_set_filename = os.path.join(output_dir,
                                                 'current_working_set.txt')

    def setup_format(self, format):
        self.format = registry[format]

    def make_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def dump(self):
        self.make_output_dir()

        database_busy_file = self.settings.get('database_busy_file')

        if database_busy_file:
            with open(database_busy_file, 'w'):
                pass

        self._drain_to_working_set()

        if database_busy_file:
            os.remove(database_busy_file)

        self._feed_input_sorters()

        with new_session() as session:
            for project_id, sorter in self.project_result_sorters.items():
                project = session.query(Project).filter_by(name=project_id).first()

                if self.settings['include_settings']:
                    self.dump_project_settings(project)

                self.dump_project(project, sorter)

                if self.settings['zip']:
                    self.zip_project(project)

        os.remove(self.working_set_filename)

    def _drain_to_working_set(self, size=1000):
        logger.info('Draining to working set %s', self.working_set_filename)

        assert not os.path.exists(self.working_set_filename)

        with new_session() as session:
            query = session.query(Result)

            if self.after:
                query = query.filter(Result.datetime > self.after)

            with open(self.working_set_filename, 'wb') as work_file:
                last_id = -1
                num_results = 0
                running = True

                while running:
                    # Optimized for SQLite scrolling window
                    rows = query.filter(Result.id > last_id).limit(size).all()

                    if not rows:
                        break

                    delete_ids = []

                    for result in rows:
                        line = base64.b64encode(pickle.dumps({
                            'id': result.id,
                            'project_id': result.project_id,
                            'shortcode': result.shortcode,
                            'url': result.url,
                            'encoding': result.encoding,
                            'datetime': result.datetime,
                        }))
                        work_file.write(line)
                        work_file.write(b'\n')

                        num_results += 1
                        self.items_count += 1

                        delete_ids.append(result.id)

                        if num_results % 10000 == 0:
                            logger.info('Drain progress: %d', num_results)

                        if self.max_items and num_results >= self.max_items:
                            logger.info('Reached max items %d.', self.max_items)
                            running = False
                            break

                    if self.settings['delete']:
                        session.execute(delete(Result).where(
                            Result.id.in_(delete_ids)))

    def _feed_input_sorters(self):
        num_results = 0

        with open(self.working_set_filename, 'rb') as work_file:
            for line in work_file:
                result = pickle.loads(base64.b64decode(line))

                if result['project_id'] not in self.project_result_sorters:
                    self.project_result_sorters[result['project_id']] = \
                        GNUExternalSort(temp_dir=self.output_dir,
                                        temp_prefix='tott-{0}-'.format(
                                            result['project_id']
                                            )
                                        )
                    self.projects_count += 1

                sorter = self.project_result_sorters[result['project_id']]
                sorter.input(
                    result['shortcode'],
                    (result['id'], result['url'], result['encoding'],
                     result['datetime'])
                )
                num_results += 1

                if num_results % 10000 == 0:
                    logger.info('Sort progress: %d', num_results)

    def dump_project(self, project, sorter):
        logger.info('Looking in project %s', project.name)

        assert project.url_template.endswith('{shortcode}'), \
            'Writer only supports URL with prefix'

        # XXX: Use regex \{shortcode\}$ instead?
        site = project.url_template.replace('{shortcode}', '')

        last_filename = None

        for i, (key, value) in enumerate(sorter.sort()):
            if i % 10000 == 0:
                logger.info('Format progress: %d/%d', i, sorter.rows)

            id_, url, encoding, datetime_ = value
            result = ResultContainer(id_, key, url, encoding, datetime_)

            # we can do this as the query is sorted
            # so that item that would end up together
            # would returned together
            filename = self.get_filename(project, result)
            if filename != last_filename:
                self.close_fp()

                logger.info('Writing results to file %s.', filename)
                assert not os.path.isfile(filename), 'Target file %s already exists' % (filename)

                self.fp = self.get_fp(filename)
                self.writer = self.format(self.fp)
                self.writer.write_header(site)

                last_filename = filename

            for encoding in (result.encoding, 'latin-1', 'cp437', 'utf-8'):
                try:
                    result.url.encode(encoding)
                except UnicodeError:
                    logger.warning('Encoding failed %s|%s %s.',
                                   result.shortcode, repr(result.url),
                                   encoding,
                                   exc_info=True)
                    continue
                else:
                    self.writer.write_shortcode(
                        result.shortcode, result.url, encoding
                    )
                    break
            else:
                raise Exception(
                    'Unable to encode {}|{} {}'
                    .format(result.shortcode, repr(result.url),
                            result.encoding)
                )

            if not self.last_date or result.datetime > self.last_date:
                self.last_date = result.datetime

        self.close_fp()

    def dump_project_settings(self, project):
        path = os.path.join(self.output_dir, project.name,
                            '{0}.meta.json.xz'.format(project.name))
        self.fp = self.get_fp(path)
        self.writer = ProjectSettingsWriter(self.fp)
        self.writer.write_project(project)
        self.close_fp()

    def zip_project(self, project):
        project_path = os.path.join(self.output_dir, project.name)

        filename = project.name

        if self.settings.get('zip_filename_infix'):
            filename += self.settings['zip_filename_infix']

        zip_path = os.path.join(self.output_dir, '{0}.zip'.format(filename))

        assert not os.path.isfile(zip_path), 'Target file %s already exists' % (zip_path)

        with zipfile.ZipFile(zip_path, mode='w',
                             compression=zipfile.ZIP_STORED) as zip_file:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_filename = os.path.relpath(file_path, self.output_dir)
                    zip_file.write(file_path, arc_filename)

        shutil.rmtree(project_path)

    def get_fp(self, filename):
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        if self.lzma:
            return lzma.open(filename, 'wb')
        else:
            return open(filename, 'wb')

    def close_fp(self):
        if not self.fp or not self.writer:
            return
        self.writer.write_footer()
        self.fp.close()

    def get_filename(self, project, item):
        path = os.path.join(self.output_dir, project.name)

        dirs, prefix, underscores = self.split_shortcode(
            item.shortcode, self.dir_length, self.max_right, self.file_length)

        dirs = [quote(dirname.encode('ascii')) for dirname in dirs]
        path = os.path.join(path, *dirs)

        path = os.path.join(path, '%s%s.%s' % (
            quote(prefix.encode('ascii')),
            '_' * len(underscores),
            self.extension
        ))

        return path

    @classmethod
    def split_shortcode(cls, shortcode, dir_length=2, max_right=4,
                        file_length=2):
        assert dir_length >= 0
        assert max_right >= 0
        assert file_length >= 0
        # 0001asdf
        # dir_length max_right file_length

        dirs = []

        # create directories until we left only max_right or less characters
        length = 0
        shortcode_temp = shortcode
        while dir_length and len(shortcode_temp) > max_right + file_length:
            dirname = shortcode_temp[:dir_length]
            dirs.append(dirname)
            length += len(dirname)
            shortcode_temp = shortcode_temp[dir_length:]

        # name the file
        code_length = len(shortcode)
        length_left = code_length - length
        underscores = min(length_left, max_right)

        return dirs, shortcode[:code_length - underscores], shortcode[code_length - underscores:]


class ExporterBootstrap(Bootstrap):
    def start(self, args=None):
        super().start(args=args)

        logging.basicConfig(level=logging.INFO)

        self.exporter = Exporter(self.args.output_dir, self.args.format, vars(self.args))
        self.exporter.dump()
        self.write_stats()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument(
            '--format', default='beacon',
            choices=registry.keys(), help='Output file format')
        self.arg_parser.add_argument(
            '--after',
            help='Only export items submitted after specified time. '
                 '(ISO8601 format YYYY-MM-DDTHH:MM:SS.mmmmmm)')
        self.arg_parser.add_argument(
            '--include-settings',
            help='Include project settings', action='store_true')
        self.arg_parser.add_argument(
            '--zip', help='Zip the projects after exporting',
            action='store_true')
        self.arg_parser.add_argument(
            '--dir-length', type=int, default=2,
            help='Number of characters per directory name'
            )
        self.arg_parser.add_argument(
            '--file-length', type=int, default=2,
            help='Number of characters per filename prefix (excluding directory names)'
            )
        self.arg_parser.add_argument(
            '--max-right', type=int, default=4,
            help='Number of characters used inside the file (excluding directory and file prefix names)'
            )
        self.arg_parser.add_argument(
            '--delete', action='store_true',
            help='Delete the exported rows after export'
            )
        self.arg_parser.add_argument(
            '--max-items', type=int, metavar='N',
            help='Export a maximum of N items.')
        self.arg_parser.add_argument(
            '--zip-filename-infix',
            help='Insert string in filename in final zip filename.'
        )
        self.arg_parser.add_argument(
            '--database-busy-file',
            help='A sentinel file to indicate the database is likely busy and locked'
        )
        self.arg_parser.add_argument(
            'output_dir', help='Output directory (will be created)')

    def write_stats(self):
        logger.info(
            'Written %d items in %d projects',
            self.exporter.items_count, self.exporter.projects_count
        )
        if self.exporter.last_date:
            logger.info('Last item timestamp (use --after to dump after this item):')
            logger.info(self.exporter.last_date.isoformat())


if __name__ == '__main__':
    ExporterBootstrap().start()
