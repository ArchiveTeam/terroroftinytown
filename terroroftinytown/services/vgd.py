import re

from terroroftinytown.client import errors
from terroroftinytown.services.isgd import IsgdService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six.moves import html_parser


class VgdService(IsgdService):
    def parse_blocked(self, response):
        try:
            return IsgdService.parse_blocked(self, response)
        except errors.UnexpectedNoResult:
            pass

        response.encoding = 'utf-8'

        match = re.search("<p>For reference and to help those fighting spam the original destination of this URL is given below \(we strongly recommend you don't visit it since it may damage your PC\): -<br />(.*)</p><h2>v\.gd</h2><p>v\.gd is a free service used to shorten long URLs\.", response.text)
        if not match:
            raise errors.UnexpectedNoResult("Could not find target URL in 'Link Disabled' page")

        url = match.group(1)
        url = html_parser.HTMLParser().unescape(url)
        if url == "":
            return (URLStatus.unavailable, None, None)
        return (URLStatus.ok, url, response.encoding)


class Vgd6Service(HashRandMixin, VgdService):
    def get_shortcode_width(self):
        return 6
