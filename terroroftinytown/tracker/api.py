# encoding=utf-8
import json
from tornado.web import HTTPError
import tornado.websocket

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.errors import (NoItemAvailable, UserIsBanned,
    InvalidClaim)
from terroroftinytown.tracker.model import Project


class ProjectSettingsHandler(BaseHandler):
    def get(self):
        name = self.get_argument('name')
        project = Project.get_plain(name)

        if project:
            self.write(project.to_dict())
        else:
            raise HTTPError(404, 'Project not found')


class LiveStatsHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        pass

    def on_close(self):
        pass


class GetHandler(BaseHandler):
    def post(self):
        ip_address = self.get_argument('ip_address', None)
        version = self.get_argument('version', None)
        username = self.get_argument('username')

        try:
            claim = self.application.checkout_item(
                username, ip_address=ip_address, version=version,
            )
        except NoItemAvailable:
            raise HTTPError(404, 'No items available')
        except UserIsBanned:
            raise HTTPError(403, 'You are banned')
        else:
            self.write(claim)


class DoneHandler(BaseHandler):
    def post(self):
        claim_id = self.get_argument('claim_id')
        tamper_key = self.get_argument('tamper_key')
        results_str = self.get_argument('results')
        results = json.loads(results_str)

        try:
            self.application.checkin_item(claim_id, tamper_key, results)
        except InvalidClaim:
            raise HTTPError(409, 'Invalid item claimed')
        else:
            self.write({'status': 'OK'})
