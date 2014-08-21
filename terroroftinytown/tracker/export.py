# encoding=utf-8

import os

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.format import registry
from terroroftinytown.tracker.model import new_session, Project, Result

class Exporter(Bootstrap):
    projects_count = 0
    items_count = 0

    def __init__(self):
        super().__init__()
        self.setup_format()
        self.dump()
        self.write_stats()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('--format', default='beacon',
            choices=registry.keys(), help='Output file format')
        self.arg_parser.add_argument('output_dir', help='Output directory (will be created)')

    def setup_format(self):
        self.format = registry[self.args.format]

    def dump(self):
        if not os.path.isdir(self.args.output_dir):
            os.mkdir(self.args.output_dir)

        with new_session() as session:
            for project in session.query(Project):
                self.dump_project(project)

    def write_stats(self):
        print('Written %d projects %d items' % (self.projects_count, self.items_count))

    def dump_project(self, project):
        base = self.mkdir(project)
        with new_session() as session:
            # TODO: Percent encoding
            # TODO: Storage tree
            # TODO: After specified time
            query = session.query(Result).filter_by(project=project)
            # XXX: Any better way that this that does not load everything to memory
            # and does not use another query?
            if query.count() == 0:
                return

            self.projects_count += 1

            fp = open(os.path.join(base, project.name + '.txt'), 'wb')
            # XXX: Use regex \{shortcode\}$ instead?
            site = project.url_template.replace('{shortcode}', '')

            writer = self.format(fp)
            writer.write_header(site)

            for item in query:
                self.items_count += 1
                writer.write_shortcode(item.shortcode, item.url, item.encoding)

            writer.write_footer()
            fp.close()


    def mkdir(self, project):
        path = os.path.join(self.args.output_dir, project.name)

        if not os.path.isdir(path):
            os.makedirs(path)

        return path

if __name__ == '__main__':
    Exporter()