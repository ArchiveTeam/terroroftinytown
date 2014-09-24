from __future__ import unicode_literals

from terroroftinytown.client.errors import UnexpectedNoResult
from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six.moves.urllib import parse as urlparse


class BitlyService(BaseService):
    def process_redirect(self, response):
        if response.status_code == 302:
            if 'location' not in response.headers:
                raise UnexpectedNoResult()

            url = urlparse.urlparse(response.headers['location'])

            if url.scheme != "http" or url.netloc != "bit.ly" or url.path != "/a/warning":
                raise UnexpectedNoResult("Unexpected Location header after HTTP status 302")

            query = urlparse.parse_qs(url.query)

            if not ("url" in query and len(query["url"]) == 1) or not ("hash" in query and len(query["hash"]) == 1):
                raise UnexpectedNoResult("Unexpected Location header after HTTP status 302")
            if query["hash"][0] != self.current_shortcode:
                raise UnexpectedNoResult("Hash mismatch for HTTP status 302")

            unshortened_url = query["url"][0]

            return (URLStatus.ok, unshortened_url, None)

        else:
            return BaseService.process_redirect(self, response)
