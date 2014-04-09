# encoding=utf-8
from wtforms import validators
from wtforms.fields.core import StringField, BooleanField, FloatField
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


class ChangePasswordForm(LoginForm):
    password = PasswordField(
        'New password:',
        [validators.Length(min=8, max=100)]
    )


class ConfirmForm(Form):
    confirm = BooleanField('Yes, proceed.', [validators.InputRequired()])


class AddProjectForm(Form):
    name = StringField(
        'Name:',
        [
            validators.Length(min=3, max=30),
            validators.Regexp(r'^[a-z0-9_-]+$')
        ]
    )


class ProjectSettingsForm(Form):
    min_version = StringField('Minimum script version:')
    alphabet = StringField(
        'Alphabet:',
        [validators.InputRequired()],
        default='0123456789abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    url_template = StringField(
        'URL template:',
        [validators.InputRequired()],
        default='http://example.com/{shortcode}'
    )
    rate_limit = FloatField(
        'Time between requests (seconds)',
        [validators.InputRequired()],
        default=0.5
    )
    redirect_codes = StringField(
        'Redirect status codes:',
        [validators.InputRequired()],
        default='301 302 303 307'
    )
    no_redirect_codes = StringField(
        'No redirect status codes:',
        [validators.InputRequired()],
        default='404'
    )
    unavailable_codes = StringField(
        'Unavailable status codes:',
        [validators.InputRequired()],
        default='200'
    )
    banned_codes = StringField(
        'Banned status codes:',
        [validators.InputRequired()],
        default='420'
    )
    body_regex = StringField('Content body regular expression:')
    custom_code_required = BooleanField('Custom script code required')
