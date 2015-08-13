from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.client.errors import UnexpectedNoResult
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six import u


class TinyurlHuService(BaseService):
    def process_redirect_body(self, response):
        try:
            return BaseService.process_redirect_body(self, response)
        except UnexpectedNoResult:
            if b'Sajn\xc3\xa1lom, de a be\xc3\xadrt URL hib\xc3\xa1s!'.decode('utf8') in response.text:
                return (URLStatus.not_found, None, None)
            else:
                raise


class TinyurlHu4Service(HashRandMixin, TinyurlHuService):
    def get_shortcode_width(self):
        return 4
