from django.conf.urls.defaults import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', 'ajax_form.views.index', name='ajax_form_index'),
)

urlpatterns += staticfiles_urlpatterns()
