'''Put the working set from the export script back into the database.'''
import logging
import pickle
import base64

from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.model import new_session, Result
from sqlalchemy.sql.expression import insert


logger = logging.getLogger(__name__)


class UndrainBootstrap(Bootstrap):
    def start(self, args=None):
        super().start(args=args)

        logging.basicConfig(level=logging.INFO)

        self.recover()

    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('working_set_file')

    def recover(self):
        logger.info('Recovering from %s', self.args.working_set_file)
        with open(self.args.working_set_file, 'r') as file, \
                new_session() as session:
            query = insert(Result)
            values = []

            for line_num, line in enumerate(file):
                doc = pickle.loads(base64.b64decode(line))

                values.append({
                    'project_id': doc['project_id'],
                    'shortcode': doc['shortcode'],
                    'url': doc['url'],
                    'encoding': doc['encoding'],
                    'datetime': doc['datetime'],
                })

                if line_num % 10000 == 0:
                    logger.info('Recover progress: %d', line_num)
                    session.execute(query, values)
                    session.commit()
                    values = []

            logger.info('Finishing up...')
            session.execute(query, values)
            session.commit()

        logger.info('Done!')


if __name__ == '__main__':
    UndrainBootstrap().start()
