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
from terroroftinytown.util.jsonutil import NativeStringJSONDecoder


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
        version = int(self.get_argument('version'))
        client_version = int(self.get_argument('client_version'))
        username = self.get_argument('username')
        user_agent = self.request.headers.get('User-Agent')

        try:
            claim = self.application.checkout_item(
                username, ip_address=ip_address, version=version,
                client_version=client_version
            )
        except NoItemAvailable:
            raise HTTPError(
                404,
                reason='No items available currently. Try again later.'
            )
        except UserIsBanned:
            raise HTTPError(
                403,
                reason='You are banned. Please contact an administrator.'
            )
        except FullClaim:
            raise HTTPError(
                429,
                reason=(
                    'No more items available for %s. '
                    'Don\'t worry; We limit 1 IP address per shortener. '
                    'Try again later.'
                    % (ip_address)
                    )
                )
        except UpdateClient as e:
            raise HTTPError(
                412,
                reason=(
                    'Client needs update. '
                    'Library version: %s (current %s), '
                    'Pipeline version: %s (current %s). '
                    'Please restart Warrior.'
                    % (
                        e.version, e.current_version,
                        e.client_version, e.current_client_version
                    )
                )
            )
        else:
            logger.info(
                'User request: ip=%s user=%s '
                'ver=%s client_ver=%s user_agent=%s',
                ip_address, repr(username),
                version, client_version, repr(user_agent)
            )
            logger.info('Checked out claim %s', claim)
            self.write(claim)


class DoneHandler(BaseHandler):
    def post(self):
        claim_id = self.get_argument('claim_id')
        tamper_key = self.get_argument('tamper_key')
        results_str = self.get_argument('results')
        results = json.loads(results_str, cls=NativeStringJSONDecoder)

        try:
            self.application.checkin_item(claim_id, tamper_key, results)
        except InvalidClaim:
            raise HTTPError(
                409,
                reason='The item is invalid or '
                       'may have been already done by someone else.'
                )
        else:
            logger.info('Checked in claim %s %s', claim_id, results)
            self.write({'status': 'OK'})


class ErrorHandler(BaseHandler):
    def post(self):
        claim_id = self.get_argument('claim_id')
        tamper_key = self.get_argument('tamper_key')
        message = self.get_argument('message')

        try:
            self.application.report_error(claim_id, tamper_key, message)
        except InvalidClaim:
            raise HTTPError(409, reason='Invalid item claimed')
        else:
            logger.info('Error reported for claim %s', claim_id)
            self.write({'status': 'OK'})
