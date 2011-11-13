from django.conf.urls.defaults import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import index

urlpatterns = patterns('',
    url(r'^$', index, name='ajax_form_index'),
)

urlpatterns += staticfiles_urlpatterns()
