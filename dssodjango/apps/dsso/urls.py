#from django.conf.urls.defaults import patterns, include, url
from django.conf.urls import patterns, url
from django.contrib import admin
#from django.contrib.auth.decorators import login_required
#from django.views.generic.simple import direct_to_template
from dssodjango.apps.dsso import views

admin.autodiscover()


urlpatterns = patterns(
    '',
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^validate_cookie', views.validate_cookie, name='validate_cookie'),
    url(r'^signout', views.signout, name='signout'),
    url(r'^api/get_credentials_from_token/(?P<token>\w+)',
        views.api_get_credentials_from_token,
        name='api_get_credentials_from_token')

    # ex: /polls/5/results/
    #url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    #url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),

    #url(r'^404/$', 'django.views.generic.simple.direct_to_template',
    #    {'template': '404.html'}),
)
