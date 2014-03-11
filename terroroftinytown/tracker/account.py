# encoding=utf-8
import tornado.gen
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import LoginForm, AddUserForm, ConfirmForm
import terroroftinytown.tracker.util


ACCOUNT_COOKIE_NAME = 'tottu'


class LoginHandler(BaseHandler):
    def get(self):
        form = LoginForm()
        self.render('admin/login.html', form=form)

    @tornado.gen.coroutine
    def post(self):
        form = LoginForm(self.request.arguments)

        if form.validate() \
        and self._login(form.username.data, form.password.data):
            self.redirect(self.get_argument('next', self.reverse_url('admin')))
            return

        yield terroroftinytown.tracker.util.sleep(1)
        self.render('admin/login.html', form=form, message='Log in failed.')

    def _login(self, username, password):
        if self.application.db.is_no_users():
            self.application.db.add_user(username, password)

        if self.application.db.is_valid_user(username, password):
            self.set_secure_cookie(
                ACCOUNT_COOKIE_NAME, username, expires_days=None
            )
            return True


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(ACCOUNT_COOKIE_NAME)
        self.redirect('/')


class AllOverviewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        usernames = self.application.db.all_usernames()

        self.render('admin/all_users.html', usernames=usernames)


class AddUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        form = AddUserForm()
        self.render('admin/user_add.html', form=form)

    @tornado.web.authenticated
    def post(self):
        form = AddUserForm(self.request.arguments)

        if form.validate():
            username = form.username.data
            password = form.password.data

            if not self.application.db.is_username_exists(username):
                self.application.db.add_user(username, password)
                self.redirect(self.reverse_url('admin'))
                return

        self.render('admin/user_add.html', form=form)


class UserOverviewHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        self.render('admin/user_overview.html', username=username)


class DeleteUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        form = ConfirmForm()
        self.render('admin/user_delete.html', username=username, form=form)

    @tornado.web.authenticated
    def post(self, username):
        form = ConfirmForm(self.request.arguments)

        if form.validate():
            self.application.db.remove_user(username)
            self.redirect(self.reverse_url('users.overview'))
        else:
            self.render('admin/user_delete.html', username=username, form=form)
