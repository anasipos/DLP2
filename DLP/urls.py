from django.conf.urls import patterns, include, url

from django.contrib import admin
from tests.views import TestView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DLP.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^tests/', include('tests.urls', namespace='tests')),

)
