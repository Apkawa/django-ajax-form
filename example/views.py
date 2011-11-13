import json
from django import forms

from django.shortcuts import render_to_response

from django.http import HttpResponse

from ajax_form.form_serializer import FormSerializer


class ExampleForm(forms.Form):
    name = forms.CharField(label='user name',
            help_text="is name", min_length=2, max_length=20)
    is_active = forms.BooleanField(initial=True)
    gender = forms.ChoiceField(choices=[('m', 'male'), ('f', 'female')])
    love_eat = forms.MultipleChoiceField(
            choices=[('meat', 'meat'), ('beer', 'beer'), ('cheese', 'cheese')])

    is_marred = forms.ChoiceField(
            choices=[('y', 'yes'), ('no', 'no')],
            widget=forms.RadioSelect(attrs={'class': 'nya'})
            )

    def clean(self):
        if not self.errors:
            raise forms.ValidationError(u"Example error in clean")
        return self.cleaned_data


def index(request):
    if request.POST:
        form = ExampleForm(data=request.POST)
    else:
        form = ExampleForm()

    if request.is_ajax():
        form_dict = FormSerializer().serialize(form)
        print form_dict
        return HttpResponse(json.dumps(form_dict))

    return render_to_response('ajax_form.html', {'form': form})
