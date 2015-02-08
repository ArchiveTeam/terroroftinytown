from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.client import VERSION
from terroroftinytown.client.errors import UnexpectedNoResult
import re
from terroroftinytown.services.status import URLStatus


class SharedByService(BaseService):
    def __init__(self, *args, **kwargs):
        BaseService.__init__(self, *args, **kwargs)
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 6.1; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/39.0.2171.95 Safari/537.36 '
            'Nintendu/64 (URLTeam {0})'
        ).format(VERSION)

    def process_redirect_body(self, response):
        try:
            return BaseService.process_redirect_body(self, response)
        except UnexpectedNoResult:
            if 'cakeErr1-context' not in response.text:
                raise

            match = re.search(
                r'"Location: (.*)"</pre>', response.text, re.DOTALL
            )

            if not match:
                raise

            link = match.group(1)
            # Python's urllib escapes too much. We'll escape the bare minimum
            link = link.replace('\n', '%0A')
            link = link.replace('\r', '%0D')

            return (URLStatus.ok, link, response.encoding)


class SharedBy6Service(HashRandMixin, SharedByService):
    def get_shortcode_width(self):
        return 6
