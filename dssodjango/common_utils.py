import datetime
#from django.conf import settings
import json
import random
import re
import urllib
from urlparse import parse_qs, urlsplit, urlunsplit
from urllib import urlencode

from configs.settings import ldap as ldap_settings
from configs.settings import urls as url_settings
from dssodjango import models

from django.contrib.auth.views import logout
from django.db import transaction, DatabaseError, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

SERVICE_TO_URL = url_settings.SERVICE_TO_URL
SSO_URL = SERVICE_TO_URL['dsso']
SSO_AUTH_URL = SSO_URL + '/api/get_credentials_from_token'
LDAP_SERVER = ldap_settings.LDAP_SERVER
LDAP_PORT = ldap_settings.LDAP_PORT
LDAP_BASE_DN = ldap_settings.LDAP_BASE_DN

# character set for token and auth_key generation
CHAR_SET = '_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class SubdomainsMiddleware:
    """
    Re-wire the URL paths based on domain.
    http://blog.101ideas.cz/posts/subdomains-in-django-an-example.html
    """
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']

        if re.match(r'^(\w+\-)?dsso', request.domain):
            #request.urlconf = 'dssodjango.dsso.urls'
            request.path = '/dsso' + request.path
            request.path_info = '/dsso' + request.path_info
        elif re.match(r'^(\w+\-)?go', request.domain):
            request.path = '/go_url' + request.path
            request.path_info = '/go_url' + request.path_info
        elif re.match(r'^(\w+\-)?who', request.domain):
            request.path = '/who' + request.path
            request.path_info = '/who' + request.path_info


def custom_reverse_url(url_name):
    """
    Drop-in replacement for the default Django reverse function.
    """
    namespace = url_name
    namespace = re.sub(r':.+', '', namespace)
    for key, mapped_url in SERVICE_TO_URL.iteritems():
        if url_name.startswith(key + ':'):
            _index_url = namespace + ':index'
            print "Reversing '%s'" % _index_url
            root_url = reverse(_index_url)
            if not root_url:
                raise RuntimeError("Programmatic Error: unable to reverse "
                                   "'%s'" % _index_url)
            root_url = root_url.rstrip('/')
            return re.sub(root_url, mapped_url, reverse(url_name))

    return reverse(url_name)
    #raise ValueError("Unknown url name '%s'" % url_name)


def get_randomized_chars(size=48):
    return ''.join([random.choice(CHAR_SET) for _ in range(size)])


def add_query_parameter(url, param_name, param_value):
    """
    http://stackoverflow.com/questions/4293460/how-to-add-custom-parameters-to-an-url-query-string-with-python
    Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://exam.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://exam.com?foo=stuff&biz=baz'
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60

    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT")

    response.set_cookie(key,
                        value,
                        max_age=max_age,
                        expires=expires,
                        #domain='172.16.238.88',
                        secure=None)  # TODO(kevinx): https


def get_app_urls():
    """
    Get a list of all the URLs in the configuration (urls.py)
    """
    urls = []
    unimportant_urls = []
    for app_name, url in SERVICE_TO_URL.iteritems():
        if app_name in ('dsso'):
            continue
        if app_name in ('better360'):
            unimportant_urls.append((app_name, url))
            continue
        urls.append((app_name, url))
    urls.extend(unimportant_urls)
    return urls


###########################################################################
# Below are common SSO utilities for applications to validate credentials
###########################################################################


def _get_sso_credentials_from_token(token):
    # TODO(kevinx): error check URL get
    _auth_url = SSO_AUTH_URL + '/' + token
    auth_info_string = urllib.urlopen(_auth_url).readlines()[0]
    try:
        return json.loads(auth_info_string)
    except ValueError as e:
        print "%s (%s)" % (e, auth_info_string)
        return None


@transaction.autocommit
def app_validate_token(request, token, app_auth_key, next_url):
    """
    Got a temporary token from SSO, now validate it
    """
    # TODO(kevinx): error check
    credentials = _get_sso_credentials_from_token(token)
    if not credentials:
        response = HttpResponseRedirect(next_url)
        response.delete_cookie(app_auth_key)
        return response

    response = HttpResponseRedirect(next_url)
    app_auth_chars = get_randomized_chars(64)
    set_cookie(response, app_auth_key, app_auth_chars)

    try:
        app_auth_obj = models.AppAuthInfo(
            app_auth_key=app_auth_chars,
            cn=credentials['cn'],
            mail=credentials['mail'],
            displayName=credentials['displayName'],
            objectSid=credentials['objectSid'])
    except DatabaseError as e:
        # pass, just store the error (could be "length too large", etc)
        transaction.rollback()
        raise e

    try:
        app_auth_obj.save()
    except IntegrityError as e:
        transaction.rollback()
        raise e

    return response


def app_validate_cookie(request, app_auth_value, next_url):
    """
    Forwarded from validate_token, make sure cookie is set.
    """
    app_auth_value = request.COOKIES.get(app_auth_value)
    if not app_auth_value:
        return HttpResponse("Please enable your cookie and "
                            "<a href=\"%s\">try again.</a>" %
                            next_url)

    response = HttpResponseRedirect(next_url)

    cn, _, _, _, _ = get_app_credentials_from_auth_value(app_auth_value)
    if not cn:
        # reset the cookie
        response.delete_cookie(app_auth_value)

    return response


def get_app_credentials_from_auth_value(app_auth_value):
    try:
        app_auth_obj = models.AppAuthInfo.objects.get(
            app_auth_key=app_auth_value)
        if app_auth_obj:
            userName = re.sub(r'@.+', '', app_auth_obj.mail)
            return (app_auth_obj.cn,
                    userName,
                    app_auth_obj.mail,
                    app_auth_obj.displayName,
                    app_auth_obj.objectSid)

    except models.AppAuthInfo.DoesNotExist:
        pass
    return None, None, None, None, None


def app_signout(request, app_auth_key):
    logout(request)
    response = HttpResponseRedirect(SSO_URL + '/signout')
    response.delete_cookie(app_auth_key)
    return response
