# encoding=utf-8
import logging

import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import BlockUsernameForm, UnblockUsernameForm, \
    DeleteAllErrorReportsForm
from terroroftinytown.tracker.model import BlockedUser, ErrorReport, Result


logger = logging.getLogger(__name__)


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Nothing useful to show for now
        self.redirect(self.reverse_url('projects.overview'))
        # self.render('admin/overview/index.html')


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


class ErrorReportsListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            'admin/overview/error_reports.html',
            error_reports=ErrorReport.all_reports(),
            delete_all_form=DeleteAllErrorReportsForm()
        )


class ErrorReportsDeleteAllHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        ErrorReport.delete_all()
        self.redirect(self.reverse_url('admin.error_reports'))


class ResultsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        offset_id = int(self.get_argument('offset_id', 0))
        results = tuple(Result.get_results(offset_id=offset_id))
        self.render(
            'admin/overview/results.html',
            count=Result.get_count(),
            results=results,
            next_offset_id=results[-1]['id'] if results else 0
        )
