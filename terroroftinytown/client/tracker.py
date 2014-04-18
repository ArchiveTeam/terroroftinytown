# encoding-utf8
'''Tracker communication.'''


class TrackerError(Exception):
    pass


class TrackerClient(object):
    def __init__(self, host, username, bind_address=None):
        self.host = host
        self.username = username
        self.bind_address = bind_address

    def get_item(self):
        pass

    def upload_item(self, result):
        pass
