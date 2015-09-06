# encoding=utf-8


class TrackerError(Exception):
    pass


class NoItemAvailable(TrackerError):
    pass


class UserIsBanned(TrackerError):
    pass


class InvalidClaim(TrackerError):
    pass


class FullClaim(TrackerError):
    pass


class UpdateClient(TrackerError):
    def __init__(self, version, client_version, current_version, current_client_version):
        super().__init__()
        self.version = version
        self.client_version = client_version
        self.current_version = current_version
        self.current_client_version = current_client_version


class NoResourcesAvailable(TrackerError):
    pass