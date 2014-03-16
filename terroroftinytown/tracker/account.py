# encoding=utf-8
import tornado.gen
from tornado.web import HTTPError
import tornado.web

from terroroftinytown.tracker.base import BaseHandler
from terroroftinytown.tracker.form import LoginForm, AddUserForm, ConfirmForm, \
    ChangePasswordForm
from terroroftinytown.tracker.model import User
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
        if User.no_users_exist():
            user = User(username=username)
            user.set_password(password)
            user.save()

        user = User.get_by(username=username)

        if user and user.check_password(password):
            self.set_secure_cookie(
                ACCOUNT_COOKIE_NAME, username, expires_days=None
            )
            return True


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(ACCOUNT_COOKIE_NAME)
        self.redirect('/')


class AllOverviewHandler(BaseHandler):
    def _get_all_usernames(self):
        users = User.query.startswith(username='').all()
        return [user.username for user in users]

    @tornado.web.authenticated
    def get(self):
        add_user_form = AddUserForm()

        self.render(
            'admin/all_users.html',
            usernames=self._get_all_usernames(),
            add_user_form=add_user_form
        )

    @tornado.web.authenticated
    def post(self):
        action = self.get_argument('action')

        if action != 'add_user':
            raise HTTPError(400, 'Unknown action')

        add_user_form = AddUserForm(self.request.arguments)

        if add_user_form.validate():
            username = add_user_form.username.data
            password = add_user_form.password.data

            user = User.get_by(username=username)

            if not user:
                user = User(username=username)
                user.set_password(password)
                user.save()
                self.redirect(self.reverse_url('admin'))
                return
            else:
                self.render(
                    'admin/all_users.html',
                    add_user_form=add_user_form,
                    usernames=self._get_all_usernames(),
                    message='User already exists.'
                )

        self.render(self.reverse_url('users.overview'))


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        delete_form = ConfirmForm()
        password_form = ChangePasswordForm()

        self.render(
            'admin/user.html',
            username=username, delete_form=delete_form,
            password_form=password_form
        )

    @tornado.web.authenticated
    def post(self, username):
        action = self.get_argument('action')
        delete_form = ConfirmForm(self.request.arguments)
        password_form = ChangePasswordForm(self.request.arguments)

        if action == 'delete':
            self._delete(username, delete_form)
        elif action == 'password':
            self._password(username, password_form)
        else:
            raise HTTPError(400, 'Unknown action')

        self.render(
            'admin/user.html',
            username=username, delete_form=delete_form,
            password_form=password_form
        )

    def _delete(self, username, form):
        if form.validate():
            user = User.get_by(username=username)
            user.delete()
            self.redirect(self.reverse_url('users.overview'))

    def _password(self, username, form):
        if form.validate():
            user = User.get_by(username=username)
            user.set_password(form.password.data)
            user.save()
            self.redirect(self.reverse_url('users.overview'))
