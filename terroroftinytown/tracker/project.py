# encoding=utf-8
from tornado.web import HTTPError
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import AddProjectForm, ProjectSettingsForm, \
    BlockUsernameForm
from terroroftinytown.tracker.model import Project


class AllProjectsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        add_project_form = AddProjectForm()
        projects = Project.all_project_names()

        self.render(
            'admin/all_projects.html',
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

            project = Project.get_by(name=name)

            if not project:
                project = Project(name=name)
                project.save()
                self.redirect(self.reverse_url('project.overview', name))
                return
            else:
                message = 'Project already exists.'

        self.render(
            'admin/all_projects.html',
            add_project_form=add_project_form,
            projects=Project.all_project_names(),
            message=message
        )


class ProjectHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)


class QueueHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)


class ClaimsHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)


class BlockedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        form = BlockUsernameForm()
        self.render(
            'admin/project_blocked.html',
            project_name=name, form=form,
            usernames=self.application.db.all_blocked_usernames()
        )

    @tornado.web.authenticated
    def post(self, name):
        form = BlockUsernameForm(self.request.arguments)

        if form.validate():
            self.application.db.block_username(form.username.data)
            self.redirect(self.reverse_url('project.overview', name))

        self.render(
            'admin/project_blocked.html', project_name=name, form=form,
            usernames=self.application.db.all_blocked_usernames()
        )


class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, name):
        form = ProjectSettingsForm()
        self.render(
            'admin/project_settings.html',
            project_name=name, form=form,
        )

    @tornado.web.authenticated
    def post(self, name):
        form = ProjectSettingsForm(self.request.arguments)

        if form.validate():
            project = Project.get_by(name=name)
            project.alphabet = form.alphabet.data
            project.min_version = form.min_version.data
            project.url_template = form.url_template.data
            project.request_delay = form.request_delay.data
            project.redirect_codes = form.redirect_codes.data
            project.no_redirect_codes = form.no_redirect_codes.data
            project.unavailable_codes = form.unavailable_codes.data
            project.banned_codes = form.banned_codes.data
            project.body_regex = form.body_regex.data
            project.custom_code_required = form.custom_code_required.data
            project.method = form.method.data
            project.save()

            self.redirect(self.reverse_url('project.overview', name))
            return

        self.render(
            'admin/project_settings.html',
            project_name=name, form=form,
            message='Error.'
        )


class DeleteHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)
