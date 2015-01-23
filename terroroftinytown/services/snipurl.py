from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class SnipurlService(BaseService):
    def process_redirect(self, response):
        url_status, link, encoding = BaseService.process_redirect(self, response)

        if link == "/site/getprivate?snip=" + self.current_shortcode:
            return URLStatus.unavailable, None, None
        else:
            return url_status, link, encoding

    # It doesn't seem like preview link handling is needed anymore?
    # The preview page seems to be only active under "peek.snipurl.com"
