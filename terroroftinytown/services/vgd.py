from terroroftinytown.services.isgd import IsgdService
from terroroftinytown.services.rand import HashRandMixin


class VgdService(IsgdService):
    pass


class Vgd6Service(HashRandMixin, VgdService):
    def get_shortcode_width(self):
        return 6
