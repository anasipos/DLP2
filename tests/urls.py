from views import ChooseTestView, PageDetailView, process_page, ResultsView

__author__ = 'anamaria.sipos'

from django.conf.urls import url, patterns

urlpatterns = patterns('',
                       url(r'^(?P<test_id>\d+)/(?P<page_id>\d+)/(?P<next_page_id>\d+)/$', process_page, name='process-page'),
                       url(r'^(?P<test_id>\d+)/(?P<page_id>\d+)/$', PageDetailView.as_view(), name='test'),
                       url(r'^results/(?P<pk>\d+)/$', ResultsView.as_view(), name='results'),
                       url(r'^$', ChooseTestView.as_view(), name='test-list'),

                       )

