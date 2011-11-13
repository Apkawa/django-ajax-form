import json
from django import forms

from django.shortcuts import render_to_response

from django.http import HttpResponse

class ExampleForm(forms.Form):
    name = forms.CharField(label='user name', help_text="is name", min_length=2, max_length=20)
    gender = forms.ChoiceField(choices=[('m', 'male'), ('f', 'female')])
    is_active = forms.BooleanField(initial=True)

    def clean(self):
        if not self.errors:
            raise forms.ValidationError(u"Example error in clean")
        return self.cleaned_data

from django.utils.encoding import smart_unicode
from django.utils.functional import Promise

class JSONForm(object):
    @staticmethod
    def is_iterator(obj):
        if isinstance(obj, (list, tuple)):
            return True
        try:
            iter(obj)
            return True
        except TypeError:
            return False

    def prepare_data(self, data, depth=None):
        depth = depth or 7

        if depth <= 0:
            return smart_unicode(data)

        if isinstance(data, basestring):
            return smart_unicode(data)

        elif isinstance(data, bool):
            return data

        elif data is None:
            return data

        elif isinstance(data, Promise):
            return unicode(data)

        elif isinstance(data, dict):
            return dict((key, self.prepare_data(value, depth - 1)) for key, value in data.iteritems())

        elif self.is_iterator(data):
            return [self.prepare_data(value, depth - 1) for value in data]

        return smart_unicode(data)

    def get_field_type(self, field):
        widget = field.widget
        if isinstance(widget, forms.Select):
            return 'select'
        elif isinstance(widget, forms.CheckboxInput):
            return 'checkbox'
        elif isinstance(widget, forms.Textarea):
            return 'textarea'
        elif isinstance(widget, forms.HiddenInput):
            return 'hidden'
        return 'text'

    def field_to_dict(self, bound_field):
        field_dict = {}
        field = bound_field.field
        for attr in ['required',
                        'label',
                        #'help_text',
                        #'error_messages',
                        'choices',
                        ]:
            if hasattr(field, attr):
                field_dict[attr] = getattr(field, attr)

        field_dict['value'] = bound_field.value()
        field_dict['label'] = bound_field.label
        field_dict['help_text'] = bound_field.help_text
        field_dict['type'] = self.get_field_type(field)
        field_dict['widget_attrs'] = bound_field.field.widget.attrs
        return field_dict

    def form_to_dict(self, form_instance):
        '''
        return {
                'fields': {'name': {
                                    'type': 'input', 'help': 'help text', 'min_length': 2}
                                    },
                'data': {'name': 'Nya', },
                                    }
        '''

        fields_dict = {}
        for name in form_instance.fields.iterkeys():
            fields_dict[name] = self.field_to_dict(form_instance[name])

        form_dict = {}
        form_dict['fields'] = fields_dict
        form_dict['data'] = form_instance.data
        form_dict['errors'] = form_instance.errors
        form_dict['initial'] = form_instance.initial
        return self.prepare_data(form_dict)


def index(request):
    if request.POST:
        form = ExampleForm(data=request.POST)
    else:
        form = ExampleForm()

    if request.is_ajax():
        form_dict = JSONForm().form_to_dict(form)
        print form_dict
        return HttpResponse(json.dumps(form_dict))

    return render_to_response('ajax_form.html', {'form': form})



