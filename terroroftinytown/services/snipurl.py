import re

from terroroftinytown.client.errors import UnhandledStatusCode, \
    UnexpectedNoResult
from terroroftinytown.services.base import BaseService, html_unescape
from terroroftinytown.services.status import URLStatus


class SnipurlService(BaseService):
    def process_redirect(self, response):
        try:
            url_status, link, encoding = BaseService.process_redirect(
                self, response)
        except UnexpectedNoResult:
            if 'Location' not in response.headers:
                return URLStatus.not_found, None, None
            else:
                raise

        if link == "/site/getprivate?snip=" + self.current_shortcode:
            return URLStatus.unavailable, None, None
        else:
            return url_status, link, encoding

    def process_unknown_code(self, response):
        first_status_code = response.status_code

        if first_status_code not in (200, 500):
            return BaseService.process_unknown_code(self, response)

        url = self.params['url_template'].format(
            shortcode=self.current_shortcode)
        response = self.fetch_url(url, 'get')
        second_status_code = response.status_code

        if second_status_code not in (200, 500):
            raise UnhandledStatusCode(
                "HTTP status changed from %s to %i on second request for %s"
                % (first_status_code, second_status_code,
                   self.current_shortcode)
                )

        pattern = "<p>You clicked on a snipped URL, which will take you to the following looong URL: </p> <div class=\"quote\"><span class=\"quotet\"></span><br/>(.*?)</div> <br />"
        match = re.search(pattern, response.text)

        if not match:
            text = response.text.replace("<br />\n", "")
            match = re.search(pattern, text)

        if not match:
            raise UnexpectedNoResult(
                "Could not find target URL on preview page for {0}"
                .format(self.current_shortcode))

        url = html_unescape(match.group(1))

        return URLStatus.ok, url, response.encoding
