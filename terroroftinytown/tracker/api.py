# encoding=utf-8
import json
import logging

from tornado.web import HTTPError
import tornado.websocket

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.errors import (NoItemAvailable, UserIsBanned,
    InvalidClaim, FullClaim, UpdateClient)
from terroroftinytown.tracker.model import Project
from terroroftinytown.tracker.stats import Stats, stats_bus


logger = logging.getLogger(__name__)


class ProjectSettingsHandler(BaseHandler):
    def get(self):
        name = self.get_argument('name')
        project = Project.get_plain(name)

        if project:
            self.write(project.to_dict())
        else:
            raise HTTPError(404, reason='Project not found')


class LiveStatsHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global stats_bus
        self.write_message({
            'live': Stats.instance.get_live(),
            'lifetime': Stats.instance.get_lifetime(),
            'global': Stats.instance.get_global(),
            'project': Stats.instance.get_project()
        })

        stats_bus += self.on_stats

    def on_stats(self, **stats):
        self.write_message({
            'live_new': stats
        })

    def on_close(self):
        stats_bus.clear_handlers(self)


class GetHandler(BaseHandler):
    def post(self):
        ip_address = self.request.remote_ip
        version = int(self.get_argument('version', -1))
        client_version = int(self.get_argument('client_version', -1))
        username = self.get_argument('username')

        try:
            claim = self.application.checkout_item(
                username, ip_address=ip_address, version=version,
                client_version=client_version
            )
        except NoItemAvailable:
            raise HTTPError(404, reason='No items available')
        except UserIsBanned:
            raise HTTPError(403, reason='You are banned. Please contact an administrator.')
        except FullClaim:
            raise HTTPError(429, reason='%s has pending claims in all eligible projects. Check that your client is up to date and contact the administrator to release any pending claims.' % (ip_address))
        except UpdateClient as e:
            raise HTTPError(412, reason='Update your client. Script version: %s (current %s), Client version: %s (current %s -- must be manually upgraded)' % (
                    e.version, e.current_version,
                    e.client_version, e.current_client_version
                )
            )
        else:
            logger.info('Checked out claim %s', claim)
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
            raise HTTPError(409, reason='Invalid item claimed')
        else:
            logger.info('Checked in claim %s %s', claim_id, results)
            self.write({'status': 'OK'})
