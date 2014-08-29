import random, hashlib, datetime

from sqlalchemy.sql.expression import insert

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.model import new_session, Result

class MockResult(Bootstrap):
    def __init__(self):
        super().__init__()
        self.generate_mock()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('--count', help='Number of items to generate', default=int(1E6), type=int)

    def generate_mock(self):
        with new_session() as session:
            items = []

            for i in range(self.args.count):
                if i % 100 == 0:
                    print(i)

                items.append({
                    'project_id': 'test',
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
    MockResult()