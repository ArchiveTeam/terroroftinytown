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
