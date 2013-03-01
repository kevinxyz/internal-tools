# coding=utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext

from dssodjango.common_utils import (
    add_query_parameter,
    app_validate_token, app_validate_cookie, app_signout,
    get_app_credentials_from_auth_value, custom_reverse_url,
    SSO_URL, get_app_urls)

APP_NAME = 'sample_app'
APP_AUTH_KEY = 'app_auth_key'


def validate_token(request, token):
    return app_validate_token(request, token, APP_AUTH_KEY,
                              custom_reverse_url(APP_NAME + ':validate_cookie'))


def validate_cookie(request):
    return app_validate_cookie(request, APP_AUTH_KEY,
                               custom_reverse_url(APP_NAME + ':index'))


def signout(request):
    return app_signout(request, APP_AUTH_KEY)


def index(request):
    """
    Main entrance page.
    """
    _, username, email, _, _ = get_app_credentials_from_auth_value(
        request.COOKIES.get(APP_AUTH_KEY, None))

    context = {
        'email': email,
        'signin_url': add_query_parameter(SSO_URL, 'service', APP_NAME),
        'signout_url': custom_reverse_url(APP_NAME + ':signout'),
        'app_urls': get_app_urls()
    }
    return render_to_response(APP_NAME + '/index.html',
                              context,
                              context_instance=RequestContext(request))
