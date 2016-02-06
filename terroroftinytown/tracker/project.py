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
from terroroftinytown.tracker.model import Project, BlockedUser, Item, Budget


logger = logging.getLogger(__name__)


class AllProjectsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        add_project_form = AddProjectForm()
        projects = Project.all_project_infos()

        self.render(
            'admin/project/all.html',
            projects=projects,
            add_project_form=add_project_form,
            project_budgets=Budget.projects,
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
                logger.info(self.user_audit_text('Created project %s'), name)
                self.redirect(self.reverse_url('project.overview', name))
                return
        else:
            message = 'Error'

        self.render(
            'admin/project/all.html',
            add_project_form=add_project_form,
            projects=Project.all_project_infos(),
            message=message,
            project_budgets=Budget.projects,
        )


class ProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, project_id):
        # Nothing useful to show for now
        self.redirect(self.reverse_url('project.claims', project_id))
        # self.render('admin/project/overview.html', project_id=name)


class QueueHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, project_id):
        project = Project.get_plain(project_id)
        enable_form = QueueEnableForm(data=self.get_enable_form(project))
        form = QueueSettingsForm(data=self.get_queue_settings_form(project))
        self.render(
            'admin/project/queue_settings.html',
            project_id=project_id,
            lower_shortcode=project.lower_shortcode(),
            form=form,
            enable_form=enable_form
        )

    @tornado.web.authenticated
    def post(self, project_id):
        project = Project.get_plain(project_id)
        enable_form = QueueEnableForm(data=self.get_enable_form(project))
        form = QueueSettingsForm(data=self.get_queue_settings_form(project))
        lower_shortcode = project.lower_shortcode()

        message = None
        action = self.get_argument('action', None)

        if action == 'enable':
            enable_form = QueueEnableForm(self.request.arguments)
            if enable_form.validate():
                with Project.get_session_object(project_id) as project:
                    project.enabled = enable_form.enabled.data
                    logger.info(self.user_audit_text('Project %s enabled=%s'),
                                project_id, project.enabled)
                    message = ('Enabled' if project.enabled else 'Disabled')
            else:
                message = 'Error in Queue Enable Form.'

        elif action == 'autoqueue':
            form = QueueSettingsForm(self.request.arguments)
            if form.validate():
                with Project.get_session_object(project_id) as project:
                    form.populate_obj(project)
                    project.lower_sequence_num = form.lower_sequence_num.data or 0
                    project.autorelease_time = form.autorelease_time.data * 60 or 0

                    lower_shortcode = project.lower_shortcode()

                logger.debug('Project %s queue settings changed.', project_id)
                message = 'Settings saved.'
            else:
                message = 'Error in Auto Queue Form.'
        else:
            message = 'Error: unrecognized action argument.'

        Budget.calculate_budgets()

        self.render(
            'admin/project/queue_settings.html',
            project_id=project_id,
            lower_shortcode=lower_shortcode,
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
    def get(self, project_id):
        delete_form = ConfirmForm()
        manual_add_form = AddItemsForm()
        release_form = ReleaseClaimForm()
        item_action_form = ItemActionForm()
        items = Item.get_items(project_id)

        self.render(
            'admin/project/claims.html', project_id=project_id,
            delete_form=delete_form,
            manual_add_form=manual_add_form,
            release_form=release_form,
            item_action_form=item_action_form,
            items=items,
        )

    @tornado.web.authenticated
    def post(self, project_id):
        delete_form = ConfirmForm(self.request.arguments)
        manual_add_form = AddItemsForm(self.request.arguments)
        release_form = ReleaseClaimForm(self.request.arguments)
        item_action_form = ItemActionForm(self.request.arguments)
        items = Item.get_items(project_id)
        action = self.get_argument('action')

        if action == 'manual_add' and manual_add_form.validate():
            self._add_items(project_id)
            self.redirect(self.reverse_url('project.claims', project_id))
            return
        elif action == 'delete_one' and item_action_form.validate():
            self._delete_one()
            self.redirect(self.reverse_url('project.claims', project_id))
            return
        elif action == 'release_one' and item_action_form.validate():
            self._release_one()
            self.redirect(self.reverse_url('project.claims', project_id))
            return
        elif action == 'release' and release_form.validate():
            self._release_all(project_id, release_form)
            self.redirect(self.reverse_url('project.claims', project_id))
        elif action == 'delete' and delete_form.validate():
            self._delete_all(project_id)
            self.redirect(self.reverse_url('project.claims', project_id))
            return

        self.render(
            'admin/project/claims.html', project_id=project_id,
            delete_form=delete_form,
            manual_add_form=manual_add_form,
            release_form=release_form,
            item_action_form=item_action_form,
            items=items,
        )

    def _add_items(self, project_id):
        items = self.get_argument('items').split()
        seq_list = []

        for item in items:
            logger.info(self.user_audit_text('Adding to project %s item'),
                        project_id)
            lower_seq_num, upper_seq_num = item.split('-')
            lower_seq_num = int(lower_seq_num)
            upper_seq_num = int(upper_seq_num)
            seq_list.append((lower_seq_num, upper_seq_num))

        Item.add_items(project_id, seq_list)
        Budget.calculate_budgets()

    def _delete_one(self):
        item_id = int(self.get_argument('id'))

        Item.delete(item_id)
        Budget.calculate_budgets()

        logger.info(self.user_audit_text('Deleted item %s'), item_id)

    def _release_one(self):
        item_id = int(self.get_argument('id'))

        Item.release(item_id)
        Budget.calculate_budgets()

        logger.info(self.user_audit_text('Released item %s'), item_id)

    def _release_all(self, project_id, release_form):
        time_ago = time.time() - release_form.hours.data * 60

        Item.release_all(project_id, datetime.datetime.utcfromtimestamp(time_ago))
        Budget.calculate_budgets()

        logger.info(self.user_audit_text('Released items for %s'), project_id)

    def _delete_all(self, project_id):
        Item.delete_all(project_id)
        Budget.calculate_budgets()

        logger.info(self.user_audit_text('Delete all items for %s'), project_id)


class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, project_id):
        project = Project.get_plain(project_id)
        form = ProjectSettingsForm(**project.to_dict())

        self.render(
            'admin/project/shortener_settings.html',
            project_id=project_id, form=form,
        )

    @tornado.web.authenticated
    def post(self, project_id):
        form = ProjectSettingsForm(self.request.arguments)
        message = None

        if form.validate():
            with Project.get_session_object(project_id) as project:
                form.populate_obj(project)

            logger.info(
                self.user_audit_text('Changed project %s shortener settings'),
                project_id)
            message = 'Settings saved.'
        else:
            message = 'Error.'

        self.render(
            'admin/project/shortener_settings.html',
            project_id=project_id, form=form,
            message=message
        )


class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, project_id):
        form = ConfirmForm()
        self.render('admin/project/delete.html', project_id=project_id, form=form)

    @tornado.web.authenticated
    def post(self, project_id):
        form = ConfirmForm(self.request.arguments)

        if form.validate():
            Project.delete_project(project_id)
            Budget.calculate_budgets()

            logger.info(self.user_audit_text('Deleted project %s'), project_id)
            self.redirect(self.reverse_url('admin.overview'))
        else:
            self.render('admin/project/delete.html', project_id=project_id, form=form)
