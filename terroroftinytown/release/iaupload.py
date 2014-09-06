import os.path

from terroroftinytown.tracker.bootstrap import Bootstrap
import internetarchive


class IAUploaderBootstrap(Bootstrap):
    def setup_args(self):
        super().setup_args()
        self.arg_parser.add_argument('directory')
        self.arg_parser.add_argument('--title', required=True)
        self.arg_parser.add_argument('--identifier', required=True)

    def start(self, args=None):
        super().start(args=args)

        directory = self.args.directory

        if not os.path.isdir(directory):
            raise Exception('Path is not a directory')

        contents = os.listdir(directory)

        for filename in contents:
            if not os.path.isfile(filename):
                raise Exception('{} is not a file'.format(filename))

        identifier = self.args.identifier
        title = self.args.title
        collection = self.config['iaexporter']['collection']
        access_key = self.config['iaexporter']['access_key'],
        secret_key = self.config['iaexporter']['secret_key'],

        assert identifier
        assert title

        item = internetarchive.get_item(identifier)
        metadata = dict(
            title=title,
            collection=collection,
            mediatype='software',
            subject='urlteam;terroroftinytown',
            description='URLTeam\'s rolling release of unshortened URLs.',
        )

        print('Begin upload', contents)

        item.upload(contents, metadata=metadata, verify=True, verbose=True,
                    access_key=access_key, secret_key=secret_key, retries=10)

        print('Done')


if __name__ == '__main__':
    bootstrap = IAUploaderBootstrap()
    bootstrap.start()
