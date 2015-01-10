from terroroftinytown.services.base import BaseService, html_unescape
import re
from terroroftinytown.services.status import URLStatus
from terroroftinytown.client.errors import UnexpectedNoResult


class AdjixService(BaseService):
    def process_redirect(self, response):
        if '<title>Spammer</title>' in response.text or \
                '<title>Phisher</title>' in response.text or \
                'It has automatically been terminated.' in response.text or \
                'This link was created by a spammer' in response.text or \
                'This link was created by an unknown spammer' in response.text or \
                'This link was abused by' in response.text or \
                '<title>Abuse</title>' in response.text or \
                '<title>Link Removed</title>' in response.text:
            return (URLStatus.unavailable, None, None)

        groups = re.findall((
            r'CONTENT="\d+;URL=(.*)(?:\r\n|">)|'
            '<frame src="(.*)(?:\r\n|">)|'
            'rel="canonical" href="(.*)"/>'
            ),
            response.text
        )

        for group in groups:
            text = group[0] or group[1] or group[2]
            link = html_unescape(text)

            if 'ad.adjix.com' in link:
                continue

            return (URLStatus.ok, link, response.encoding)

        raise UnexpectedNoResult(
            "Didn't get anything for {0}".format(self.current_shortcode))
