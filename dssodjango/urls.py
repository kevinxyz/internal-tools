#from django.conf.urls.defaults import patterns, include, url
from django.conf.urls import patterns, include, url
from django.contrib import admin
#from django.contrib.auth.decorators import login_required
#from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.conf.urls.static import static
from configs.common import PROJECT_PATH

admin.autodiscover()


urlpatterns = patterns(
    '',
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^sample_app/', include('dssodjango.apps.sample_app.urls',
                                 namespace='sample_app')),
    url(r'^dsso/', include('dssodjango.apps.dsso.urls',
                           namespace='dsso')),
    url(r'^go_url/', include('dssodjango.apps.go_url.urls',
                             namespace='go_url')),
    url(r'^who/', include('dssodjango.apps.who.urls',
                          namespace='who')),
    url(r'^better360/', include('dssodjango.apps.better360.urls',
                                namespace='better360')),
    url(r'^roulette/', include('dssodjango.apps.roulette.urls',
                               namespace='roulette')),

    #url(r'^$', include('dsso.urls'), name='dsso'),

    #url(r'^$', views.index, name='index'),
    #url(r'^query$', views.query, name='query'),

    # ex: /polls/5/results/
    #url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    #url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),

    #url(r'^404/$', 'django.views.generic.simple.direct_to_template',
    #    {'template': '404.html'}),

    # 'static(...)' is not necessary in runserver mode, but is required when
    # used with uwsgi
) + static(settings.STATIC_URL,
           document_root='%s/dssodjango/static' % PROJECT_PATH)
