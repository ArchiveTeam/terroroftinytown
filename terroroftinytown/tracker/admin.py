# encoding=utf-8
import logging

import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import BlockUsernameForm, UnblockUsernameForm, \
    DeleteAllErrorReportsForm, AutoDeleteErrorReportsForm
from terroroftinytown.tracker.model import BlockedUser, ErrorReport, Result,\
    GlobalSetting
from tornado.web import HTTPError


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
        offset_id = int(self.get_argument('offset_id', 0))
        error_reports = ErrorReport.all_reports(offset_id=offset_id)
        auto_delete_form = AutoDeleteErrorReportsForm(
            enabled=GlobalSetting.get_value(
                GlobalSetting.AUTO_DELETE_ERROR_REPORTS)
        )

        self.render(
            'admin/overview/error_reports.html',
            error_reports=error_reports,
            delete_all_form=DeleteAllErrorReportsForm(),
            auto_delete_form=auto_delete_form,
            next_offset_id=error_reports[-1]['id'] if error_reports else 0,
            count=ErrorReport.get_count()
        )


class ErrorReportsDeleteAllHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        form = DeleteAllErrorReportsForm(self.request.arguments)

        if form.validate():
            ErrorReport.delete_all()
            self.redirect(self.reverse_url('admin.error_reports'))
        else:
            raise HTTPError(400)


class AutoDeleteErrorReportsSettingHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        form = AutoDeleteErrorReportsForm(self.request.arguments)

        if form.validate():
            GlobalSetting.set_value(
                GlobalSetting.AUTO_DELETE_ERROR_REPORTS, form.enabled.data
            )
            self.redirect(self.reverse_url('admin.error_reports'))
        else:
            raise HTTPError(400)


class ResultsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        args = {k: self.get_argument(k, default) for (k, default) in [('offset_id', 0), ('limit',1000), ('project_id',None)]}
        results = tuple(Result.get_results(**args))
        self.render(
            'admin/overview/results.html',
            count=Result.get_count(args['project_id']),
            results=results,
            next_higher_offset_id=int(results[0]['id'])+int(args['limit']) if results else 0,
            next_lower_offset_id=int(results[-1]['id'])-1 if results else 0,
            **args)
