# encoding=utf-8
import datetime
import logging
import time

from sqlalchemy.exc import IntegrityError
from tornado.web import HTTPError
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import AddProjectForm, ProjectSettingsForm, \
    BlockUsernameForm, UnblockUsernameForm, QueueSettingsForm, ConfirmForm, \
    AddItemsForm, ReleaseClaimForm, ItemActionForm, QueueEnableForm
from terroroftinytown.tracker.model import Project, BlockedUser, Item


logger = logging.getLogger(__name__)


class AllProjectsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        add_project_form = AddProjectForm()
        projects = Project.all_project_names()

        self.render(
            'admin/project/all.html',
            projects=projects,
            add_project_form=add_project_form,
        )

    @tornado.web.authenticated
    def post(self):
        action = self.get_argument('action')
        message = None

        if action != 'add_project':
            raise HTTPError(400, 'Unknown action')

        add_project_form = AddProjectForm(self.request.arguments)

        if add_project_form.validate():
            name = add_project_form.name.data

            try:
                Project.new_project(name)
            except IntegrityError:
                message = 'Project already exists.'
            else:
                logger.info('Created project %s', name)
                self.redirect(self.reverse_url('project.overview', name))
                return

        self.render(
            'admin/project/all.html',
            add_project_form=add_project_form,
            projects=Project.all_project_names(),
            message=message
        )


class ProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        self.render('admin/project/overview.html', project_name=name)


class QueueHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        project = Project.get_plain(name)
        enable_form = QueueEnableForm(data=self.get_enable_form(project))
        form = QueueSettingsForm(data=self.get_queue_settings_form(project))
        self.render(
            'admin/project/queue_settings.html',
            project_name=name,
            form=form,
            enable_form=enable_form
        )

    @tornado.web.authenticated
    def post(self, name):
        project = Project.get_plain(name)
        enable_form = QueueEnableForm(data=self.get_enable_form(project))
        form = QueueSettingsForm(data=self.get_queue_settings_form(project))

        message = None
        action = self.get_argument('action', None)

        if action == 'enable':
            enable_form = QueueEnableForm(self.request.arguments)
            if enable_form.validate():
                with Project.get_session_object(name) as project:
                    project.enabled = enable_form.enabled.data
                    logger.info('Project %s enabled=%s',
                                name, project.enabled)
            else:
                message = 'Error.'

        elif action == 'autoqueue':
            form = QueueSettingsForm(self.request.arguments)
            if form.validate():
                with Project.get_session_object(name) as project:
                    project.autoqueue = form.autoqueue.data
                    project.num_count_per_item = form.num_count_per_item.data
                    project.max_num_items = form.max_num_items.data
                    project.lower_sequence_num = form.lower_sequence_num.data or 0
                    project.autorelease_time = form.autorelease_time.data * 60 or 0

                logger.debug('Project %s queue settings changed.', name)
                message = 'Settings saved.'
            else:
                message = 'Error.'
        else:
            message = 'Error.'

        self.render(
            'admin/project/queue_settings.html',
            project_name=name,
            form=form,
            enable_form=enable_form,
            message=message
        )

    def get_enable_form(self, project):
        return {
            'enabled': project.enabled,
        }

    def get_queue_settings_form(self, project):
        return {
            'autoqueue': project.autoqueue,
            'num_count_per_item': project.num_count_per_item,
            'max_num_items': project.max_num_items,
            'lower_sequence_num': project.lower_sequence_num,
            'autorelease_time': project.autorelease_time // 60
        }


class ClaimsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        delete_form = ConfirmForm()
        manual_add_form = AddItemsForm()
        release_form = ReleaseClaimForm()
        item_action_form = ItemActionForm()
        items = Item.get_items(name)

        self.render(
            'admin/project/claims.html', project_name=name,
            delete_form=delete_form,
            manual_add_form=manual_add_form,
            release_form=release_form,
            item_action_form=item_action_form,
            items=items,
        )

    @tornado.web.authenticated
    def post(self, name):
        delete_form = ConfirmForm(self.request.arguments)
        manual_add_form = AddItemsForm(self.request.arguments)
        release_form = ReleaseClaimForm(self.request.arguments)
        item_action_form = ItemActionForm(self.request.arguments)
        items = Item.get_items(name)
        action = self.get_argument('action')

        if action == 'manual_add' and manual_add_form.validate():
            self._add_items(name)
            self.redirect(self.reverse_url('project.claims', name))
            return
        elif action == 'delete_one' and item_action_form.validate():
            self._delete_one()
            self.redirect(self.reverse_url('project.claims', name))
            return
        elif action == 'release_one' and item_action_form.validate():
            self._release_one()
            self.redirect(self.reverse_url('project.claims', name))
            return
        elif action == 'release' and release_form.validate():
            self._release_all(name, release_form)
            self.redirect(self.reverse_url('project.claims', name))
        elif action == 'delete' and delete_form.validate():
            self._delete_all(name)
            self.redirect(self.reverse_url('project.claims', name))
            return

        self.render(
            'admin/project/claims.html', project_name=name,
            delete_form=delete_form,
            manual_add_form=manual_add_form,
            release_form=release_form,
            item_action_form=item_action_form,
            items=items,
        )

    def _add_items(self, name):
        items = self.get_argument('items').split()
        seq_list = []

        for item in items:
            logger.info('Adding to project %s item', name)
            lower_seq_num, upper_seq_num = item.split('-')
            lower_seq_num = int(lower_seq_num)
            upper_seq_num = int(upper_seq_num)
            seq_list.append((lower_seq_num, upper_seq_num))

        Item.add_items(name, seq_list)

    def _delete_one(self):
        item_id = int(self.get_argument('id'))
        Item.delete(item_id)
        logger.info('Deleted item %s', item_id)

    def _release_one(self):
        item_id = int(self.get_argument('id'))
        Item.release(item_id)
        logger.info('Released item %s', item_id)

    def _release_all(self, project_name, release_form):
        time_ago = time.time() - release_form.hours.data * 60
        Item.release_all(project_name, datetime.datetime.utcfromtimestamp(time_ago))
        logger.info('Released items for %s', project_name)

    def _delete_all(self, project_name):
        Item.delete_all(project_name)
        logger.info('Delete all items for %s', project_name)


class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        project = Project.get_plain(name)
        form = ProjectSettingsForm(
            alphabet=project.alphabet,
            banned_codes=project.banned_codes,
            body_regex=project.body_regex,
            method=project.method,
            min_version=project.min_version,
            min_client_version=project.min_client_version,
            no_redirect_codes=project.no_redirect_codes,
            redirect_codes=project.redirect_codes,
            request_delay=project.request_delay,
            url_template=project.url_template,
            unavailable_codes=project.unavailable_codes,
        )

        self.render(
            'admin/project/shortener_settings.html',
            project_name=name, form=form,
        )

    @tornado.web.authenticated
    def post(self, name):
        form = ProjectSettingsForm(self.request.arguments)
        message = None

        if form.validate():
            with Project.get_session_object(name) as project:
                project.alphabet = form.alphabet.data
                project.min_version = form.min_version.data
                project.min_client_version = form.min_client_version.data
                project.url_template = form.url_template.data
                project.request_delay = form.request_delay.data
                project.redirect_codes = form.redirect_codes.data
                project.no_redirect_codes = form.no_redirect_codes.data
                project.unavailable_codes = form.unavailable_codes.data
                project.banned_codes = form.banned_codes.data
                project.body_regex = form.body_regex.data
                project.method = form.method.data

            logger.info('Changed project %s shortener settings', name)
            message = 'Settings saved.'
        else:
            message = 'Error.'

        self.render(
            'admin/project/shortener_settings.html',
            project_name=name, form=form,
            message=message
        )


class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        form = ConfirmForm()
        self.render('admin/project/delete.html', project_name=name, form=form)

    @tornado.web.authenticated
    def post(self, name):
        form = ConfirmForm(self.request.arguments)

        if form.validate():
            Project.delete_project(name)
            logger.info('Deleted project %s', name)
            self.redirect(self.reverse_url('admin.overview'))
        else:
            self.render('admin/project/delete.html', project_name=name, form=form)
