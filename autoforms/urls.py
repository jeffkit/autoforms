#encoding=utf-8
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^$','autoforms.views.index'),
    (r'^jsi18n/$','autoforms.views.jsi18n'),
	(r'^preview/$','autoforms.views.preview'),
	(r'^preview/(?P<id>\d+)/$','autoforms.views.preview'),
	url(r'^fill/(?P<id>\d+)/$','autoforms.views.fill_with_id',name="form-fill-old"),
	url(r'^(?P<user>[\w-]+)/(?P<slug>[\w-]+)/$','autoforms.views.fill_with_slug',name="form-fill"),
)
