# encoding=utf-8

import os, lzma
import shutil
import zipfile

from sqlalchemy import func

from terroroftinytown.format import registry
from terroroftinytown.format.projectsettings import ProjectSettingsWriter
from terroroftinytown.format.urlformat import quote
from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.model import new_session, Project, Result


class Exporter:
    def __init__(self, output_dir, format="beacon", settings={}):
        super().__init__()

        self.setup_format(format)
        self.output_dir = output_dir
        self.settings = settings
        self.after = self.settings['after']

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

    def setup_format(self, format):
        self.format = registry[format]

    def make_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def dump(self):
        self.make_output_dir()

        with new_session() as session:
            for project in session.query(Project):
                if self.settings['include_settings']:
                    self.dump_project_settings(project)

                self.dump_project(project, session)

                if self.settings['zip']:
                    self.zip_project(project)

    def dump_project(self, project, session):
        print('Looking in project %s' % (project.name))
        query = session.query(Result) \
            .filter_by(project=project) \
            .order_by(func.char_length(Result.shortcode), Result.shortcode)

        if self.after:
            query = query.filter(Result.datetime > self.after)

        count = query.count()
        if count == 0:
            return

        self.projects_count += 1

        assert project.url_template.endswith('{shortcode}'), \
            'Writer only supports URL with prefix'

        # XXX: Use regex \{shortcode\}$ instead?
        site = project.url_template.replace('{shortcode}', '')

        self.fp = None
        self.writer = None
        last_filename = ''
        i = 0

        for item in query:
            self.items_count += 1
            i += 1

            if i % 1000 == 0:
                print('%d/%d' % (i, count))

            # we can do this as the query is sorted
            # so that item that would end up together
            # would returned together
            filename = self.get_filename(project, item)
            if filename != last_filename:
                self.close_fp()

                assert not os.path.isfile(filename), 'Target file %s already exists' % (filename)

                self.fp = self.get_fp(filename)
                self.writer = self.format(self.fp)
                self.writer.write_header(site)

                last_filename = filename

            self.writer.write_shortcode(item.shortcode, item.url, item.encoding)

            if not self.last_date or item.datetime > self.last_date:
                self.last_date = item.datetime

            if self.settings['delete']:
                session.delete(item)

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
        zip_path = os.path.join(self.output_dir,
                                '{0}.zip'.format(project.name))

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

        dirs = [quote(dirname.encode(item.encoding)) for dirname in dirs]
        path = os.path.join(path, *dirs)

        path = os.path.join(path, '%s%s.%s' % (
            quote(prefix.encode(item.encoding)),
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
            'output_dir', help='Output directory (will be created)')

    def write_stats(self):
        print('Written %d items in %d projects' % (self.exporter.projects_count, self.exporter.items_count))
        if self.exporter.last_date:
            print('Last item timestamp (use --after to dump after this item):')
            print(self.exporter.last_date.isoformat())


if __name__ == '__main__':
    ExporterBootstrap().start()
