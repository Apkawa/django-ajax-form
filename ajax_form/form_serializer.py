# -*- coding: utf-8 -*-
from django import forms

from django.utils.encoding import smart_unicode, force_unicode
from django.utils.functional import Promise
from django.utils.datastructures import SortedDict

class FormSerializer(object):
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
            return force_unicode(data)

        elif isinstance(data, dict):
            return dict((key, self.prepare_data(value, depth - 1)) for key, value in data.iteritems())

        elif self.is_iterator(data):
            return [self.prepare_data(value, depth - 1) for value in data]

        return smart_unicode(data)

    def get_field_type(self, field):
        widget = field.widget

        if isinstance(widget, forms.SelectMultiple):
            return 'selectmultiple'
        if isinstance(widget, forms.RadioSelect):
            return 'radio'
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
        field_dict['id'] = bound_field.auto_id
        field_dict['id_for_label'] = bound_field.id_for_label
        field_dict['help_text'] = bound_field.help_text
        field_dict['type'] = self.get_field_type(field)
        field_dict['widget_attrs'] = bound_field.field.widget.attrs
        return field_dict

    def serialize(self, form_instance):
        fields_dict = SortedDict()
        for name in form_instance.fields.iterkeys():
            fields_dict[name] = self.field_to_dict(form_instance[name])

        form_dict = {}
        form_dict['fields'] = fields_dict
        form_dict['data'] = form_instance.data
        form_dict['errors'] = form_instance.errors
        return self.prepare_data(form_dict)
