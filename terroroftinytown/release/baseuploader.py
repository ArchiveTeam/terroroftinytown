import os.path

from terroroftinytown.tracker.bootstrap import Bootstrap


class BaseUploaderBootstrap(Bootstrap):
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

        filenames = [os.path.join(directory, filename)
                     for filename in os.listdir(directory)]

        for filename in filenames:
            if not os.path.isfile(filename):
                raise Exception('{} is not a file'.format(filename))

        identifier = self.args.identifier
        title = self.args.title
        collection = self.config['iaexporter']['collection']
        access_key = self.config['iaexporter']['access_key']
        secret_key = self.config['iaexporter']['secret_key']
        description = self.config['iaexporter']['description']

        assert identifier
        assert title
        assert collection
        assert access_key
        assert secret_key
        assert description

        self.identifier = identifier
        self.title = title
        self.collection = collection
        self.access_key = access_key
        self.secret_key = secret_key
        self.description = description
        self.filenames = filenames

        self.upload()

    def upload(self):
        raise NotImplementedError()
