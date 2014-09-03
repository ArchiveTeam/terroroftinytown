'''Instead of sequential shortcodes, generate pseudorandom shortcodes.

See https://github.com/ArchiveTeam/tinyback/blob/master/tinyback/generators.py
for historical details.
'''


class ChainMixin:
    def get_shortcode_width(self):
        raise NotImplementedError('Please override me with an integer.')

    def transform_sequence_num(self, sequence_num):
        # TODO: write me
        raise NotImplementedError('todo: not yet implemented')
