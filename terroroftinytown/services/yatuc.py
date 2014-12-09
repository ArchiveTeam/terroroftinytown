from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class YatucService(BaseService):
    def process_redirect(self, response):
        status, url, encoding = BaseService.process_redirect(self, response)

        if url == 'http://yatuc.com':
            return URLStatus.not_found, None, None
        else:
            return status, url, encoding
