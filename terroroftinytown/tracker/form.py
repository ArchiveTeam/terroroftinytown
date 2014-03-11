# encoding=utf-8
from wtforms import validators
from wtforms.fields.core import StringField, BooleanField
from wtforms.fields.simple import PasswordField

from wtforms_tornado import Form


class LoginForm(Form):
    username = StringField(
        'Username:',
        [
            validators.Length(min=3, max=30),
            validators.Regexp(r'^[a-z0-9_-]+$')
        ]
    )
    password = PasswordField('Password:', [validators.Length(min=8, max=100)])


class AddUserForm(LoginForm):
    pass


class ConfirmForm(Form):
    confirm = BooleanField('Yes, proceed.', [validators.InputRequired()])
