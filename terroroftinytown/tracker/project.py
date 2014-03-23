# encoding=utf-8
from tornado.web import HTTPError
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import AddProjectForm
from terroroftinytown.tracker.model import Project


class AllProjectsHandler(BaseHandler):
    def _get_all_project_names(self):
        projects = Project.query.startswith(name='').all()
        return [project.name for project in projects]

    @tornado.web.authenticated
    def get(self):
        add_project_form = AddProjectForm()
        projects = self._get_all_project_names()

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
            projects=self._get_all_project_names(),
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
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)


class SettingsHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)


class DeleteHandler(BaseHandler):
    def get(self, name):
        self.render('admin/project_overview.html', project_name=name)
