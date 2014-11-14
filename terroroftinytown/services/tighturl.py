from terroroftinytown.services.base import BaseService
from terroroftinytown.client.errors import UnexpectedNoResult
from terroroftinytown.services.status import URLStatus


class TighturlService(BaseService):
    def process_redirect(self, response):
        try:
            return BaseService.process_redirect(self, response)
        except UnexpectedNoResult:
            return (URLStatus.not_found, None, None)
