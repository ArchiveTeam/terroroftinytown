from __future__ import unicode_literals

from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus


class XCOService(BaseService):
    def process_redirect(self, response):
        status, url, encoding = BaseService.process_redirect(self, response)

        if status == URLStatus.ok:
            if url == 'http://www.godaddy.com/default.aspx?isc=xcowebgd':
                return URLStatus.not_found, None, None

        return status, url, encoding
