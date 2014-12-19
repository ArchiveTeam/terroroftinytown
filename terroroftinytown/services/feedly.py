from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.services.status import URLStatus


class FeedlyService(BaseService):
    def process_redirect(self, response):
        status, url, encoding = BaseService.process_redirect(self, response)

        if url == 'http://feedly.com/':
            return URLStatus.not_found, None, None
        else:
            return status, url, encoding


class Feedly8Service(HashRandMixin, FeedlyService):
    def get_shortcode_width(self):
        return 8
