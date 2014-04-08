# encoding=utf-8


class ScraperError(Exception):
    pass


class UnhandledStatusCode(ScraperError):
    pass


class UnexpectedNoResult(ScraperError):
    pass


class PleaseRetry(ScraperError):
    pass
