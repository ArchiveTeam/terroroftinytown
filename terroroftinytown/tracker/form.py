# encoding=utf-8
from wtforms import validators
from wtforms.fields.core import StringField, BooleanField, FloatField, Field, \
    IntegerField, RadioField
from wtforms.fields.simple import PasswordField, TextAreaField
from wtforms.widgets.core import TextInput
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
    min_version = IntegerField('Minimum library version:', [validators.Optional()])
    min_client_version = IntegerField('Minimum pipeline version:', [validators.Optional()])
    alphabet = StringField('Alphabet:', [validators.InputRequired()])
    url_template = StringField(
        'URL template:',
        [
            validators.InputRequired(),
            validators.Regexp(
                '^https?://.+/{shortcode}',
                message='Template does not look like a URL template.'),
        ]
    )
    request_delay = FloatField(
        'Time between requests (seconds)',
        [validators.InputRequired()]
    )
    method = RadioField(
        'HTTP method (get/head):',
        [validators.InputRequired()],
        choices=[('head', 'head'), ('get', 'get')]
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
    location_regex = StringField('Location header regular expression:')

class BlockUsernameForm(Form):
    username = StringField(
        'Usernames or IP addresses:', [validators.InputRequired()]
    )


class UnblockUsernameForm(Form):
    pass


class QueueEnableForm(Form):
    enabled = BooleanField('Enabled')


class QueueSettingsForm(Form):
    autoqueue = BooleanField('AutoQueue')
    num_count_per_item = IntegerField('Number of URLs per item:')
    max_num_items = IntegerField('Maximum number of items in todo queue:')
    lower_sequence_num = IntegerField(
        'Lower sequence number:', [validators.Optional()]
    )
    autorelease_time = IntegerField(
        'AutoRelease items after minutes:', [validators.Optional()]
    )


class AddItemsForm(Form):
    items = TextAreaField('Sequence numbers:')


class ReleaseClaimForm(Form):
    hours = IntegerField('Release claims older than minutes:')


class ItemActionForm(Form):
    pass


class DeleteAllErrorReportsForm(Form):
    pass


class AutoDeleteErrorReportsForm(Form):
    enabled = BooleanField('Automatically delete orphaned error reports.')


class CalculatorForm(Form):
    number_1 = StringField(
        'Number', [validators.Length(min=0, max=100)]
    )
    alphabet_1 = StringField(
        'Alphabet', [validators.Length(min=1, max=100)],
        default='0123456789'
    )
    number_2 = StringField(
        'Number', [validators.Length(min=0, max=100)]
    )
    alphabet_2 = StringField(
        'Alphabet', [validators.Length(min=1, max=100)],
        default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
