# encoding=utf-8
import tornado.escape
import tornado.web


class FormUIModule(tornado.web.UIModule):
    def render(self, form, action='', method='post', submit=None):
        strings = [
            '<form action="{action}" method="{method}">'.format(
                action=action, method=method),
            self.handler.xsrf_form_html()
        ]

        for field in form:
            strings.append('<div class="form-field">')

            if field.type == 'BooleanField':
                strings.append(field())
                strings.append(field.label())
            else:
                strings.append(field.label())
                strings.append(field())

            strings.append('</div>')

            for error in field.errors:
                strings.append('<div class="form-error">')
                strings.append(tornado.escape.xhtml_escape(error))
                strings.append('</div>')

        if submit:
            strings.append('<button>')
            strings.append(tornado.escape.xhtml_escape(submit))
            strings.append('</button>')

        strings.append('</form>')

        return ''.join(strings)
