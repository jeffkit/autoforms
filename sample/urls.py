from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sample.views.home', name='home'),
    # url(r'^sample/', include('sample.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
