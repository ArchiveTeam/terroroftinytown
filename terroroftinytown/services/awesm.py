from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class AwesmService(BaseService):
    def process_redirect(self, response):
        status, url, encoding = BaseService.process_redirect(self, response)

        if url.startswith('http://totally.awe.sm/') and \
                url.endswith(self.current_shortcode):
            return URLStatus.not_found, None, None
        else:
            return status, url, encoding
