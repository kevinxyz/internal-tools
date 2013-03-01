# coding=utf-8
from django.http import HttpResponseRedirect

from configs.common import get_config_value

from dssodjango.common_utils import (
    add_query_parameter,
    app_validate_token, app_validate_cookie, app_signout,
    get_app_credentials_from_auth_value, custom_reverse_url,
    SSO_URL)

APP_NAME = 'roulette'
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

    if username and email:
        # signed in, now forward to the roulette port
        url = get_config_value('urls.ROULETTE_SERVER')
        return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(
            add_query_parameter(SSO_URL, 'service', APP_NAME))
