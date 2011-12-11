# -*- coding: utf-8 -*-
from django import forms
from django.forms import formsets

from django.utils.encoding import smart_unicode, force_unicode
from django.utils.functional import Promise


class FormSerializer(object):

    def __init__(self, defaults=None):
        self._defaults = defaults

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
            return dict((key, self.prepare_data(value, depth - 1))
                                    for key, value in data.iteritems())

        elif self.is_iterator(data):
            return [self.prepare_data(value, depth - 1) for value in data]

        return smart_unicode(data)

    @staticmethod
    def is_instance_of_class(instance, cls):
        if isinstance(cls, (tuple, list)):
            for _cls in cls:
                if FormSerializer.is_instance_of_class(instance. _cls):
                    return True
            return False
        return instance.__class__ is cls

    def _get_override_type(self, field):
        if callable(self._defaults):
            return self._defaults

    def get_field_type(self, field):
        widget = field.widget

        override_type = self._get_override_type(field)
        if override_type is not None:
            return override_type

        if isinstance(widget, forms.SelectMultiple):
            return 'selectmultiple'

        elif isinstance(widget, forms.RadioSelect):
            return 'radio'

        elif isinstance(widget, forms.Select):
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
        for attr in ['required', 'label', 'choices']:
            if hasattr(field, attr):
                field_dict[attr] = getattr(field, attr)

        field_dict['value'] = bound_field.value()
        field_dict['label'] = bound_field.label
        field_dict['html_name'] = bound_field.html_name
        field_dict['id'] = bound_field.auto_id
        field_dict['id_for_label'] = bound_field.id_for_label
        field_dict['help_text'] = bound_field.help_text
        field_dict['type'] = self.get_field_type(field)
        field_dict['widget_attrs'] = bound_field.field.widget.attrs
        return field_dict

    def form_to_dict(self, form_instance):
        fields_dict = {}
        for name in form_instance.fields.iterkeys():
            field = form_instance[name]
            fields_dict[name] = self.field_to_dict(field)

        form_dict = {}
        form_dict['fields'] = fields_dict
        #form_dict['data'] = form_instance.data
        form_dict['errors'] = form_instance.errors
        return self.prepare_data(form_dict)

    def formset_to_dict(self, formset):
        formset_data = []
        formset_data.append(self.form_to_dict(formset.management_form))
        for form in formset.forms:
            formset_data.append(self.form_to_dict(form))
        return formset_data

    def serialize(self, form_instance):
        if isinstance(form_instance, forms.Form):
            return self.form_to_dict(form_instance)
        if isinstance(form_instance, formsets.BaseFormSet):
            return self.formset_to_dict(form_instance)
