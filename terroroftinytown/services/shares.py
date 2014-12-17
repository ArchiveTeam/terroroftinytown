from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class SharesService(BaseService):
    def process_redirect_body(self, response):
        if response.status_code == 301 and 'Location' not in response.headers:
            return (URLStatus.not_found, None, None)

        return BaseService.process_redirect_body(self, response)
