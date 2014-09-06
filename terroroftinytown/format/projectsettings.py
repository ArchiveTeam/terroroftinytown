'''Serialize project settings.'''
import json

from terroroftinytown.format.base import BaseWriter


class ProjectSettingsWriter(BaseWriter):
    def write_project(self, project):
        text = json.dumps(project.to_dict())
        self.fp.write(text.encode('utf-8'))

    def write_shortcode(self, shortcode, url, encoding):
        raise Exception('This method is not used.')
