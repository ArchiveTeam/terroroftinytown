from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class MyspAcService(BaseService):
    def process_redirect(self, response):
        status, link, encoding = BaseService.process_redirect(self, response)

        if link in ('https://myspace.com/404', 'http://myspace.com/404'):
            return URLStatus.not_found, None, None

        else:
            return status, link, encoding
