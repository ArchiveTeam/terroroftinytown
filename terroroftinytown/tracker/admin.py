# encoding=utf-8
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import BlockUsernameForm, UnblockUsernameForm
from terroroftinytown.tracker.model import BlockedUser


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
                BlockedUser.unblock_username(self.get_argument('username'))
                message = 'User unblocked.'

        else:
            if form.validate():
                BlockedUser.block_username(form.username.data)
                message = 'User blocked.'

        self.render(
            'admin/overview/banned.html',
            message=message,
            form=form, unblock_form=unblock_form,
            usernames=BlockedUser.all_blocked_usernames(),
        )
