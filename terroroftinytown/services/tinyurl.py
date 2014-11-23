import logging
import re
import sys

from terroroftinytown.client.errors import UnexpectedNoResult, \
    UnhandledStatusCode, PleaseRetry
from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six.moves import html_parser
from terroroftinytown.six.moves.urllib import parse as urlparse


_logger = logging.getLogger(__name__)


class TinyurlService(BaseService):
    def process_redirect(self, response):
        if response.status_code == 200:
            return self._fetch_200(response)
        else:
            if 'Location' in response.headers and response.status_code == 301:
                tiny = response.headers.get("X-tiny")

                if tiny and tiny[:3] == "aff":
                    return self._preview(
                        self.current_shortcode, response.headers['Location']
                    )

            try:
                return BaseService.process_redirect(self, response)
            except UnexpectedNoResult:
                return (URLStatus.unavailable, None, None)

    def _fetch_200(self, response):
        new_response = self.fetch_url(response.url, method='get')

        new_response.encoding = 'utf-8'

        if new_response.status_code != 200:
            raise PleaseRetry(
                'Strange 200 change to {0} for {1}'.format(
                    new_response.status_code, repr(response.url))
            )

        if "<title>Redirecting...</title>" in new_response.text:
            return self._parse_errorhelp(new_response)
        elif "Error: TinyURL redirects to a TinyURL." in new_response.text:
            return self._parse_tinyurl_redirect(new_response)
        else:
            raise UnhandledStatusCode(
                'Unhandled 200 change to {0} for {1}'.format(
                    new_response.status_code, repr(response.url))
            )

    def _parse_errorhelp(self, response):
        match = re.search('<meta http-equiv="refresh" content="0;url=(.*?)">', response.text)

        if not match:
            raise UnexpectedNoResult("No redirect on \"errorhelp\" page on HTTP status 200 for {0}".format(response.url))

        url = urlparse.urlparse(match.group(1))

        if url.scheme != "http" or url.netloc != "tinyurl.com" or url.path != "/errorb.php":
            raise UnexpectedNoResult("Unexpected redirect on \"errorhelp\" page  on HTTP status 200 for {0}".format(response.url))

        if sys.version_info[0] == 2:
            query = urlparse.parse_qs(url.query.encode('utf-8'))
        else:
            query = urlparse.parse_qs(url.query)

        if not ("url" in query and len(query["url"]) == 1) or not ("path" in query and len(query["path"]) == 1):
            raise UnexpectedNoResult("Unexpected redirect on \"errorhelp\" page  on HTTP status 200 for {0}".format(response.url))

        if query["path"][0] != ("/" + self.current_shortcode):
            raise UnexpectedNoResult("Code mismatch on \"errorhelp\" on HTTP status 200")

        if sys.version_info[0] == 2:
            result_url = query["url"][0].decode('utf-8')
        else:
            result_url = query["url"][0]

        return (URLStatus.ok, result_url, response.encoding)

    def _parse_tinyurl_redirect(self, response):
        match = re.search("<p class=\"intro\">The URL you followed redirects back to a TinyURL and therefore we can't directly send you to the site\\. The URL it redirects to is <a href=\"(.*?)\">", response.text, re.DOTALL)

        if not match:
            raise UnexpectedNoResult("No redirect on \"tinyurl redirect\" page on HTTP status 200 for {0}".format(response.url))

        url = match.group(1)

        return (URLStatus.ok, html_parser.HTMLParser().unescape(url), response.encoding)

    def _preview(self, code, affiliate_url):
        response = self.fetch_url("http://tinyurl.com/preview.php?num=" + code, method='get')

        if response.status_code != 200:
            raise UnexpectedNoResult("Unexpected HTTP status %i on preview page %s" % (response.status_code, response.url))

        match = re.search("<a id=\"redirecturl\" href=\"(.*?)\">Proceed to this site.</a>", response.text, re.DOTALL)

        if not match:
            raise UnexpectedNoResult("No redirect on preview page {0}".format(response.url))

        url = match.group(1)

        if url == "":
            return self._scrub_url(code, affiliate_url)

        return (URLStatus.ok, html_parser.HTMLParser().unescape(url), response.encoding)

    def _scrub_url(self, code, url):
        parsed_url = urlparse.urlparse(url)

        if parsed_url.hostname == "redirect.tinyurl.com" and parsed_url.path == "/api/click":
            if sys.version_info[0] == 2:
                query = urlparse.parse_qs(parsed_url.query.encode('latin-1'))
            else:
                query = urlparse.parse_qs(parsed_url.query, encoding='latin-1')

            if query["out"]:
                if sys.version_info[0] == 2:
                    scrubbed_url = query["out"][0].decode('latin-1')
                else:
                    scrubbed_url = query["out"][0]

                return (URLStatus.ok, scrubbed_url, 'latin-1')

        return (URLStatus.ok, url, 'latin-1')


class Tinyurl7Service(HashRandMixin, TinyurlService):
    def get_shortcode_width(self):
        return 7
