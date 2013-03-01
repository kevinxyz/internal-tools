# coding=utf-8
from django.db.models import F, Max
import itertools
import random
import re

from django.db import transaction
from django.db.utils import IntegrityError, DatabaseError
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader, Context
from django.shortcuts import render_to_response
from django.template import RequestContext
from configs.settings import constants

from dssodjango import models
from dssodjango.common_utils import (
    add_query_parameter,
    app_validate_token, app_validate_cookie, app_signout,
    get_app_credentials_from_auth_value, custom_reverse_url,
    SSO_URL, get_app_urls)

RESERVED_SHORT_URLS = (
    'go_url',
    'validate_token', 'validate_cookie', 'signout', 'update_entry')
CHAR_SET = 'abcdefghijklmnpqrstuvwxyz123456789'  # omit o, 0
APP_AUTH_KEY = 'app_auth_key'


class GoUrlException(Exception):
    pass


def validate_token(request, token):
    return app_validate_token(request, token, APP_AUTH_KEY,
                              custom_reverse_url('go_url:validate_cookie'))


def validate_cookie(request):
    return app_validate_cookie(request, APP_AUTH_KEY,
                               custom_reverse_url('go_url:index'))


def signout(request):
    return app_signout(request, APP_AUTH_KEY)


def index(request):
    """
    Main entrance page.
    """
    _, username, email, _, _ = get_app_credentials_from_auth_value(
        request.COOKIES.get(APP_AUTH_KEY, None))

    long_url = request.POST.get('long_url', None)
    short_url = request.POST.get('short_url', None)
    go_url = custom_reverse_url('go_url:index')
    # get popular URLs
    message = None
    if username and long_url:
        try:
            update_entry(long_url, short_url, username)
            message = "Added %s as %s%s" % (long_url, go_url, short_url)
        except GoUrlException as e:
            message = e.message

    top_urls = get_top_urls()
    context = {
        'go_url': go_url,
        'signin_url': add_query_parameter(SSO_URL, 'service', 'go_url'),
        'signout_url': custom_reverse_url('go_url:signout'),
        'company_nickname': constants.COMPANY_NICKNAME,
        'app_urls': get_app_urls(),
        'email': email,
        'message': message,
        'short_url': request.GET.get('short_url', ''),
        'top_urls': top_urls,
    }
    return render_to_response('go_url/index.html',
                              context,
                              context_instance=RequestContext(request))


def get_new_random_short_url(url_len=5):
    """
    Get a new randomized short URL that is not already on the system
    """
    tries = 12
    while True:
        short_url = ''.join([random.choice(CHAR_SET) for _ in range(url_len)])
        try:
            models.URL.objects.get(short_url=short_url)
        except models.URL.DoesNotExist:
            return short_url
        tries -= 1
        if tries == 0:
            tries = 12
            url_len += 1


@transaction.autocommit
def update_entry(long_url, short_url, username):
    long_url = re.sub(r'^\s+', '', long_url)
    long_url = re.sub(r'\s+$', '', long_url)
    if not re.match(r'https?://', long_url, flags=re.IGNORECASE):
        raise GoUrlException('URL must precede with http://...')

    long_url_exists = True
    try:
        url_objs = models.URL.objects.filter(long_url=long_url)
        # TODO(kevinx): long URL already exists! Ask if user really wants to add
    except models.URL.DoesNotExist:
        long_url_exists = False
        url_objs = None

    if short_url:
        short_url = re.sub('[^\w\-\#\/]', '', short_url)
        try:
            url_obj = models.URL.objects.get(short_url=short_url)
            if url_obj and url_obj.username.lower() != username.lower():
                raise GoUrlException("Short URL '%s' is owned by %s" %
                                     (short_url, username))
        except models.URL.DoesNotExist:
            url_obj = None

    if short_url in RESERVED_SHORT_URLS:
        raise GoUrlException("You cannot use reserved URLs.")

    if not short_url:
        if long_url_exists:
            # user attempts to add an existing URL without a new short url
            raise GoUrlException("URL '%s' already exists as %s!" %
                                 (long_url,
                                  [url_obj.short_url for url_obj in url_objs]))
        else:
            short_url = get_new_random_short_url()

    if not url_obj:
        try:
            url_obj = models.URL(long_url=long_url,
                                 short_url=short_url,
                                 username=username)
        except DatabaseError as e:
            transaction.rollback()
            raise GoUrlException(e.message)
    else:
        url_obj.long_url = long_url

    try:
        url_obj.save()
    except IntegrityError as e:
        print "Unable to save url (%s => %s): %s" % (long_url, short_url, e)
        transaction.rollback()
        raise GoUrlException(e.message)


def get_top_urls():
    max_id = models.URL.objects.all().aggregate(Max('id'))['id__max']
    recently_added_urls = models.URL.objects.filter(id__gt=max_id - 5)
    recently_clicked_urls = models.URL.objects.order_by('updated_at')[:5]
    popular_urls = models.URL.objects.order_by('total_clicks')[:5]

    urls = []
    seen_urls = set()
    for url in list(itertools.chain.from_iterable(
            (recently_added_urls, recently_clicked_urls, popular_urls))):
        if url in seen_urls:
            continue
        urls.append(url)
        seen_urls.add(url)
    return urls


def jump_url(request, short_url):
    short_url = short_url.rstrip('/')
    try:
        url_obj = models.URL.objects.get(short_url=short_url)
    except models.URL.DoesNotExist:
        return HttpResponseRedirect(add_query_parameter(
            custom_reverse_url('go_url:index'), 'short_url', short_url))

    obj = models.URL.objects.filter(id=url_obj.id)
    obj.update(total_clicks=F('total_clicks') + 1)
    obj.update(last_month_clicks=F('last_month_clicks') + 1)
    obj.update(decayed_clicks=F('decayed_clicks') + 1)

    return HttpResponseRedirect(url_obj.long_url)
