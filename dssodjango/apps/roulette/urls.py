from django.conf.urls import patterns, url
from django.contrib import admin

from dssodjango.apps.roulette import views

admin.autodiscover()


urlpatterns = patterns(
    '',
    # The token/cookie/signout pages are necessory for SSO
    url(r'^validate_token/(?P<token>\w+)',
        views.validate_token, name='validate_token'),
    url(r'^validate_cookie',
        views.validate_cookie, name='validate_cookie'),
    url(r'^signout', views.signout, name='signout'),

    url(r'^$', views.index, name='index'),
)
