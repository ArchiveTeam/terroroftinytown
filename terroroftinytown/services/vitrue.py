from terroroftinytown.services.base import BaseService


class VitrueService(BaseService):
    def fetch_url(self, url):
        return BaseService.fetch_url(self, url + '?passthru=1')
