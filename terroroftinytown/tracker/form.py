# encoding=utf-8
from wtforms import validators
from wtforms.fields.core import StringField, BooleanField, FloatField, Field, \
    IntegerField
from wtforms.fields.simple import PasswordField
from wtforms.widgets.core import TextInput, TextArea
from wtforms_tornado import Form


class NumListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ' '.join([str(data) for data in self.data])
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [int(x.strip()) for x in valuelist[0].split()]
        else:
            self.data = []


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
    alphabet = StringField('Alphabet:', [validators.InputRequired()])
    url_template = StringField('URL template:', [validators.InputRequired()])
    request_delay = FloatField(
        'Time between requests (seconds)',
        [validators.InputRequired()]
    )
    method = StringField(
        'HTTP method (get/head):',
        [validators.InputRequired()]
    )
    redirect_codes = NumListField(
        'Redirect status codes:',
        [validators.InputRequired()]
    )
    no_redirect_codes = NumListField(
        'No redirect status codes:',
        [validators.InputRequired()]
    )
    unavailable_codes = NumListField(
        'Unavailable status codes:',
    )
    banned_codes = NumListField(
        'Banned status codes:',
    )
    body_regex = StringField('Content body regular expression:')
    custom_code_required = BooleanField('Custom script code required')


class BlockUsernameForm(Form):
    username = StringField(
        'Usernames or IP addresses:', [validators.InputRequired()]
    )


class UnblockUsernameForm(Form):
    pass


class QueueSettingsForm(Form):
    enabled = BooleanField('Enabled')
    num_count_per_item = IntegerField('Number of URLs per item:')
    max_num_items = IntegerField('Maximum number of items in todo queue:')
    autoqueue = BooleanField('AutoQueue')
    lower_sequence_num = IntegerField(
        'Lower sequence number:', [validators.Optional()]
    )
