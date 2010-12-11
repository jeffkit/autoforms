#encoding=utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^jsi18n/$','autoforms.views.jsi18n'),
	(r'^preview/$','autoforms.views.preview'),
	(r'^preview/(?P<id>\d+)/$','autoforms.views.preview'),
	(r'^fill/(?P<id>\d+)/$','autoforms.views.fill'),
)
