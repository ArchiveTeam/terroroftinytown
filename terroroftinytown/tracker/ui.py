# encoding=utf-8
import tornado.escape
import tornado.web


class FormUIModule(tornado.web.UIModule):
    def render(self, form, action='', method='post', submit=None, submit_sm=False):
        strings = [
            '<form action="{action}" method="{method}" class="form-horizontal" role="form">'.format(
                action=action, method=method),
            self.handler.xsrf_form_html()
        ]

        for field in form:
            error = ' has-error' if len(field.errors) > 0 else ''

            strings.append('<div class="form-group'+error+'">')

            if field.type == 'BooleanField':
                strings.append('<div class="col-sm-offset-2"><div class="checkbox">')
                strings.append(field())
                strings.append(field.label())
                strings.append('</div></div>')
            else:
                strings.append(field.label(class_='control-label col-sm-2'))
                strings.append('<div class="col-sm-10">')
                strings.append(field(class_='form-control'))
                for error in field.errors:
                    strings.append('<div class="text-danger">')
                    strings.append(tornado.escape.xhtml_escape(error))
                    strings.append('</div>')
                strings.append('</div>')

            strings.append('</div>')

        if submit:
            btn_sm = ' btn-sm' if submit_sm else ''
            strings.append('<button class="btn btn-primary'+btn_sm+'">')
            strings.append(tornado.escape.xhtml_escape(submit))
            strings.append('</button>')

        strings.append('</form>')

        return ''.join(strings)
