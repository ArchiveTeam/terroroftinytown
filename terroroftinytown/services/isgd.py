# encoding=utf-8
from __future__ import unicode_literals

import re
import time

from terroroftinytown.client import errors
from terroroftinytown.client.errors import PleaseRetry
from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six.moves import html_parser


# __all__ = ['IsgdService']
class IsgdService(BaseService):
    # NOTE: VgdService inherits from this class!

    # unavailable status code: 200 410
    # banned status code: 502
    
    def __init__(self, *args, **kwargs):
        BaseService.__init__(self, *args, **kwargs)
        self._processing_phishing_page = False

    def scrape_one(self, sequence_number):
        self._processing_phishing_page = False
        return BaseService.scrape_one(self, sequence_number)

    def process_unavailable(self, response):
        if not response.text:
            return (URLStatus.unavailable, None, None)
        if '<div id="main"><p>Rate limit exceeded - please wait 1 minute before accessing more shortened URLs</p></div>' in response.text:
            raise PleaseRetry()
        if "<div id=\"disabled\"><h2>Link Disabled</h2>" in response.text:
            return self.parse_blocked(response)
        if "<p>The full original link is shown below. <b>Click the link</b> if you'd like to proceed to the destination shown:" in response.text:
            return self.parse_preview(response)
        if '<title>Suspected phishing site | CloudFlare</title>' in response.text:
            return self.process_phishing(response)

        raise errors.UnexpectedNoResult("Could not find processing unavailable for %s" % self.current_shortcode)

    def parse_blocked(self, response):
        response.encoding = 'utf-8'

        match = re.search("<p>For reference and to help those fighting spam the original destination of this URL is given below \(we strongly recommend you don't visit it since it may damage your PC\): -<br />(.*)</p><h2>is\.gd</h2><p>is\.gd is a free service used to shorten long URLs\.", response.text)
        if not match:
            raise errors.UnexpectedNoResult("Could not find target URL in 'Link Disabled' page")

        url = match.group(1)
        url = html_parser.HTMLParser().unescape(url)
        if url == "":
            return (URLStatus.unavailable, None, None)
        return (URLStatus.ok, url, response.encoding)

    def parse_preview(self, response):
        response.encoding = 'utf-8'

        match = re.search("<b>Click the link</b> if you'd like to proceed to the destination shown: -<br /><a href=\"(.*)\" class=\"biglink\">", response.text)
        if not match:
            raise errors.UnexpectedNoResult("Could not find target URL in 'Preview' page")

        url = match.group(1)
        return (URLStatus.ok, html_parser.HTMLParser().unescape(url), response.encoding)
    
    def process_phishing(self, response):
        if self._processing_phishing_page:
            raise errors.UnexpectedNoResult("Alreadying processing phishing page for %s" % self.current_shortcode)
        
        self._processing_phishing_page = True
        time.sleep(1)
        
        match = re.search(r'<input type="hidden" name="atok" value="([a-z0-9]+)">', response.text)
        
        url = 'https://is.gd/cdn-cgi/phish-bypass?u=/{0}&atok={1}'.format(
            self.current_shortcode, match.group(1))
        
        response = self.fetch_url(url)
        return self.process_response(response)


class Isgd6Service(HashRandMixin, IsgdService):
    def get_shortcode_width(self):
        return 6
