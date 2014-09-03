'''URL status for testing the services.'''


class URLStatus(object):
    ok = 'ok'
    '''Found a URL.'''

    not_found = 'notfound'
    '''Did not find a URL.'''

    unavailable = 'blocked'
    '''URL is blocked or unavailable such as a DCMA notice.'''
