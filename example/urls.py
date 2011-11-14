from django.conf.urls.defaults import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import index, ajax_formset

urlpatterns = patterns('',
    url(r'^$', index, name='ajax_form_index'),
    url(r'^formset/$', ajax_formset, name='ajax_form_index'),
)

urlpatterns += staticfiles_urlpatterns()
