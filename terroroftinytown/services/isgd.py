# encoding=utf-8
from __future__ import unicode_literals

import re

from terroroftinytown.client import errors
from terroroftinytown.client.errors import PleaseRetry
from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus
from terroroftinytown.six.moves import html_parser


__all__ = ['IsgdService']


class IsgdService(BaseService):
    # unavailable status code: 200 410
    # banned status code: 502

    def process_unavailable(self, response):
        if not response.text:
            return (URLStatus.unavailable, None, None)
        if '<div id="main"><p>Rate limit exceeded - please wait 1 minute before accessing more shortened URLs</p></div>' in response.text:
            raise PleaseRetry()
        if "<div id=\"disabled\"><h2>Link Disabled</h2>" in response.text:
            return self.parse_blocked(response)
        if "<p>The full original link is shown below. <b>Click the link</b> if you'd like to proceed to the destination shown:" in response.text:
            return self.parse_preview(response)

    def parse_blocked(self, response):
        match = re.search("<p>For reference and to help those fighting spam the original destination of this URL is given below \(we strongly recommend you don't visit it since it may damage your PC\): -<br />(.*)</p><h2>is\.gd</h2><p>is\.gd is a free service used to shorten long URLs\.", response.text)
        if not match:
            raise errors.UnexpectedNoResult("Could not find target URL in 'Link Disabled' page")

        url = match.group(1)
        url = html_parser.HTMLParser().unescape(url)
        if url == "":
            return (URLStatus.unavailable, None, None)
        return (URLStatus.ok, url, response.encoding)

    def parse_preview(self, response):
        match = re.search("<b>Click the link</b> if you'd like to proceed to the destination shown: -<br /><a href=\"(.*)\" class=\"biglink\">", response.text)
        if not match:
            raise errors.UnexpectedNoResult("Could not find target URL in 'Preview' page")

        url = match.group(1)
        return (URLStatus.ok, html_parser.HTMLParser().unescape(url), response.encoding)
