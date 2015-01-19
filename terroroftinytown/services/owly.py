import re

from terroroftinytown.client.errors import UnexpectedNoResult
from terroroftinytown.services.base import BaseService, html_unescape
from terroroftinytown.services.status import URLStatus


class OwlyService(BaseService):
    def process_unknown_code(self, response):
        if response.status_code != 200:
            return BaseService.process_unknown_code(self, response)

        url = self.params['url_template'].format(shortcode=self.current_shortcode)
        response = self.fetch_url(url, 'get')

        if response.status_code != 200:
            raise UnexpectedNoResult(
                "Didn't get OK on second try. Got {0} for {1}"
                .format(response.status_code, self.current_shortcode)
                )

        # Copied form tinyback. I don't think code will reach here anymore

        match = re.search(
            "<a class=\"btn ignore\" href=\"(.*?)\" title=",
            html_unescape(response.text)
        )

        if not match:
            raise UnexpectedNoResult(
                "Didn't get match on second try for {0}"
                .format(self.current_shortcode)
            )

        return (URLStatus.ok, match.group(1), response.encoding)
