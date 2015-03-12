from terroroftinytown.services.base import BaseService, html_unescape
import re
from terroroftinytown.client.errors import UnexpectedNoResult
from terroroftinytown.services.status import URLStatus


class AlturlService(BaseService):
    def process_unavailable(self, response):
        if response.status_code != 410:
            return BaseService.process_unavailable(self, response)

        match = re.search(r'was forwarding to: <BR> <font color=red>(.*)</font>', response.text)

        if not match:
            raise UnexpectedNoResult(
                "Could not find target URL on blocked page for {0}"
                .format(self.current_shortcode))

        url = html_unescape(match.group(1))

        return URLStatus.ok, url, response.encoding
