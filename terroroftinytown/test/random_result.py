import random, hashlib, datetime

from sqlalchemy.sql.expression import insert

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.database import Database
from terroroftinytown.tracker.model import new_session, Result, Project


class MockProject(Bootstrap):
    def __init__(self, delete_everything=False):
        super().__init__()
        self.delete_everything = delete_everything

    def setup_database(self):
        self.database = Database(
            path=self.config['database']['path'],
            delete_everything=self.delete_everything
        )

    def start(self, args=None):
        super().start(args=args)

        self.generate_mock()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('--count', help='Number of projects to generate', default=1, type=int)

    def generate_mock(self):
        with new_session() as session:
            for project_num in range(1, self.args.count + 1):
                project_id = 'test_{}'.format(project_num)

                project = Project(name=project_id)

                print('Running insertion')
                session.add(project)


class MockResult(Bootstrap):
    def start(self, args=None):
        super().start(args=args)

        self.generate_mock()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('--count', help='Number of items to generate', default=int(1E6), type=int)
        self.arg_parser.add_argument('--projects', help='Number of projects to generate', default=1, type=int)

    def generate_mock(self):
        with new_session() as session:
            items = []

            for i in range(self.args.count):
                if i % 100 == 0:
                    print(i)

                if self.args.projects == 1:
                    project_id = 'test'
                else:
                    project_id = 'test_{}'.format(random.randint(1, self.args.projects))

                items.append({
                    'project_id': project_id,
                    'shortcode': self.generate_shortcode(),
                    'url': self.generate_url(),
                    'encoding': 'ascii',
                    'datetime': datetime.datetime.utcnow()
                })

            print('Running insertion')
            session.execute(insert(Result), items)

    def generate_shortcode(self):
        # todo: non duplicated
        return hashlib.md5(str(random.random()).encode('ascii')).hexdigest()[:random.randrange(1, 9)]

    def generate_url(self):
        return 'http://' + self.generate_shortcode() + '.com/' + self.generate_shortcode()

if __name__ == '__main__':
    MockResult().start()
