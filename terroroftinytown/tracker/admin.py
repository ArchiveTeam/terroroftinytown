# encoding=utf-8
import logging

import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import BlockUsernameForm, UnblockUsernameForm
from terroroftinytown.tracker.model import BlockedUser


logger = logging.getLogger(__name__)


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('admin/overview/index.html')


class BannedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        form = BlockUsernameForm()
        unblock_form = UnblockUsernameForm(self.request.arguments)

        self.render(
            'admin/overview/banned.html',
            form=form, unblock_form=unblock_form,
            usernames=BlockedUser.all_blocked_usernames()
        )

    @tornado.web.authenticated
    def post(self):
        action = self.get_argument('action', None)
        form = BlockUsernameForm(self.request.arguments)
        unblock_form = UnblockUsernameForm(self.request.arguments)
        message = None

        if action == 'remove':
            if unblock_form.validate():
                username = self.get_argument('username')
                logger.info('Unblocked "%s"', username)
                BlockedUser.unblock_username(username)
                message = 'User unblocked.'

        else:
            if form.validate():
                username = form.username.data
                logger.info('Blocked "%s"', username)
                BlockedUser.block_username(username)
                message = 'User blocked.'

        self.render(
            'admin/overview/banned.html',
            message=message,
            form=form, unblock_form=unblock_form,
            usernames=BlockedUser.all_blocked_usernames(),
        )
