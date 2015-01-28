from terroroftinytown.services.base import BaseService
from terroroftinytown.services.rand import HashRandMixin
from terroroftinytown.client import VERSION


class SharedByService(BaseService):
    def __init__(self, *args, **kwargs):
        BaseService.__init__(self, *args, **kwargs)
        self.user_agent = (
            'Mozilla/5.0 (Windows NT 6.1; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/39.0.2171.95 Safari/537.36 '
            'Nintendu/64 (URLTeam {0})'
        ).format(VERSION)


class SharedBy6Service(HashRandMixin, SharedByService):
    def get_shortcode_width(self):
        return 6
