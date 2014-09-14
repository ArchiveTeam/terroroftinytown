# encoding=utf-8


class ScraperError(Exception):
    '''Generic scraper error.'''


class UnhandledStatusCode(ScraperError):
    '''The current code does not know what to do with the status code.'''


class UnexpectedNoResult(ScraperError):
    '''The code definitely expected a URL but didn't find one.'''


class PleaseRetry(ScraperError):
    '''We are banned and should try again later.'''
