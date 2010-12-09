#encoding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^jsi18n/$','autoforms.views.jsi18n'),
	(r'^form_preview/$','autoforms.views.form_preview'),
	(r'^form_preview/(?P<id>\d+)/$','autoforms.views.form_preview'),
)
