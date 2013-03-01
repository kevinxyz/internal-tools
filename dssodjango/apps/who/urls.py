from django.conf.urls import patterns, url
from django.contrib import admin

from dssodjango.apps.who import views

admin.autodiscover()


urlpatterns = patterns(
    '',
    # The token/cookie/signout pages are necessory for SSO
    url(r'^validate_token/(?P<token>\w+)',
        views.validate_token, name='validate_token'),
    url(r'^validate_cookie',
        views.validate_cookie, name='validate_cookie'),
    url(r'^signout', views.signout, name='signout'),

    url(r'^percent$', views.percent, name='percent'),
    url(r'^percentpost$', views.percentpost, name='percentpost'),
    url(r'^(?P<query>[\w\.\-\ \@\+]+)$', views.index, name='index_query'),
    url(r'^$', views.index, name='index'),
    #url(r'^$', views.index, name='index'),
)
