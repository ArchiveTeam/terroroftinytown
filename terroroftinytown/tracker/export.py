# encoding=utf-8

import os, lzma

from sqlalchemy import func

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.format import registry
from terroroftinytown.format.urlformat import quote
from terroroftinytown.tracker.model import new_session, Project, Result

class Exporter:
    projects_count = 0
    items_count = 0
    last_date = None

    output_dir = ''
    settings = {}

    lzma = True
    extension = 'txt.xz'

    # Length of directory name
    dir_length = 2
    # Number of characters from the right are not used in directory name
    # in other words, number of _
    max_right = 4
    # Number of characters from the left that are used in file name
    # in other words, number of characters that are not in directory name and not _
    file_length = 2

    # Example of settings:
    # dir_length = 2
    # max_right = 4
    # file_length = 2
    # output: projectname/00/01/000100____.txt, projectname/01/01__.txt

    after = None

    def __init__(self, output_dir, format="beacon", settings={}):
        self.setup_format(format)
        self.output_dir = output_dir
        self.settings = settings
        self.after = self.settings['after']

    def setup_format(self, format):
        self.format = registry[format]

    def make_output_dir(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def dump(self):
        self.make_output_dir()

        with new_session() as session:
            for project in session.query(Project):
                self.dump_project(project)

    def dump_project(self, project):
        print('Looking in project %s' % (project.name))
        with new_session() as session:
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

                    # assert not os.path.isfile(filename), 'Target file %s already exists' % (filename)

                    self.fp = self.get_fp(filename)
                    self.writer = self.format(self.fp)
                    self.writer.write_header(site)

                    last_filename = filename

                self.writer.write_shortcode(item.shortcode, item.url, item.encoding)

                if not self.last_date or item.datetime > self.last_date:
                    self.last_date = item.datetime

            self.close_fp()

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

        #0001asdf
        # dir_length max_right file_length
        shortcode = item.shortcode

        # create directories until we left only max_right or less characters
        length = 0
        while len(shortcode) > self.max_right + self.file_length:
            dirname = shortcode[:2]
            length += len(dirname)
            path = os.path.join(path, quote(dirname.encode(item.encoding)))
            shortcode = shortcode[2:]

        # name the file
        code_length = len(item.shortcode)
        length_left = code_length - length
        underscores = min(length_left, self.max_right)
        path = os.path.join(path, '%s%s.%s' % (
            quote(item.shortcode[:code_length - underscores].encode(item.encoding)),
            '_' * underscores,
            self.extension
        ))

        return path

class ExporterBootstrap(Bootstrap):
    def start(self):
        super().start()

        self.exporter = Exporter(self.args.output_dir, self.args.format, vars(self.args))
        self.exporter.dump()
        self.write_stats()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('--format', default='beacon',
            choices=registry.keys(), help='Output file format')
        self.arg_parser.add_argument('--after', help='Only export items submitted after specified time. (ISO8601 format YYYY-MM-DDTHH:MM:SS.mmmmmm)')
        self.arg_parser.add_argument('output_dir', help='Output directory (will be created)')

    def write_stats(self):
        print('Written %d items in %d projects' % (self.exporter.projects_count, self.exporter.items_count))
        if self.exporter.last_item:
            print('Last item timestamp (use --after to dump after this item):')
            print(self.exporter.last_date.isoformat())
    

if __name__ == '__main__':
    ExporterBootstrap().start()
