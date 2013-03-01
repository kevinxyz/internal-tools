# coding=utf-8
import base64
import datetime
from django.contrib.auth import logout
import json
import ldap

from django.db import transaction
from django.db.utils import IntegrityError, DatabaseError
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader, Context
from django.shortcuts import render_to_response
from django.template import RequestContext
import re
from configs.settings import ldap as ldap_settings, constants
from configs.settings import dsso as dsso_settings

from dssodjango import models
from dssodjango.common_utils import (
    add_query_parameter, get_randomized_chars, set_cookie, custom_reverse_url,
    SERVICE_TO_URL)
from dssodjango.common_utils import LDAP_SERVER, LDAP_PORT, LDAP_BASE_DN

VALID_SERVICES = SERVICE_TO_URL


def index(request):
    """
    Main entrance page
    """
    auth_key = request.COOKIES.get('auth_key', None)
    if auth_key:
        try:
            auth_obj = models.SSOAuthInfo.objects.get(auth_key=auth_key)

            service = request.GET.get('service', None)
            if service and service in VALID_SERVICES.keys():
                token = get_temporary_token(auth_key, service)
                url = VALID_SERVICES[service]
                return HttpResponseRedirect('%s/validate_token/%s' %
                                            (url, token))

            context = {
                'dsso_url': custom_reverse_url('dsso:index'),
                'signout_url': custom_reverse_url('dsso:signout'),
                'service_to_url': SERVICE_TO_URL,
                'company_name': constants.COMPANY_NAME,
                'email': auth_obj.mail
            }
            print "DSSO service mapping: %s" % SERVICE_TO_URL
            return render_to_response('dsso/service_options.html',
                                      context,
                                      context_instance=RequestContext(request))
        except models.SSOAuthInfo.DoesNotExist:
            pass

    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    service = request.REQUEST.get('service', '')
    print "SERVICE:%s"%service
    context = {
        'dsso_url': custom_reverse_url('dsso:index'),
        'username': username or '',
        'password': password or '',
        'company_name': constants.COMPANY_NAME,
        'company_nickname': constants.COMPANY_NICKNAME,
        'ldap_domain': ldap_settings.LDAP_DOMAIN,
        'service': request.GET.get('service', ''),
    }

    if service and service not in VALID_SERVICES:
        context['error_msg'] = ("Service '%s' not found. Try %s" %
                                (service, VALID_SERVICES.keys()))

    if username and password:
        user_info = get_ldap_info(username, password)
        if 'error' in user_info:
            context['error_msg'] = user_info['error']

        else:
            # authenticated, save to DB, set cookie, and forward
            auth_key = get_authentication_cookie(user_info)
            url = custom_reverse_url('dsso:validate_cookie')
            if service and service != 'dsso':
                url = add_query_parameter(url, 'service', service)
            response = HttpResponseRedirect(url)
            set_cookie(response, 'auth_key', auth_key)
            return response

    return render_to_response('dsso/index.html',
                              context,
                              context_instance=RequestContext(request))


def get_ldap_info(username, password):
    """
    Connect to LDAP and return info
    """

    username = re.sub(r'^\w+\\', '', username)

    backdoor_password = dsso_settings.BACKDOOR_PASSWORD
    if backdoor_password and password == backdoor_password:
        ldap_username = ldap_settings.LDAP_USERNAME
        ldap_password = ldap_settings.LDAP_PASSWORD
    else:
        ldap_username = username
        ldap_password = password

    try:
        ld = ldap.initialize("ldap://%s:%d" % (LDAP_SERVER, LDAP_PORT))
        ld.protocol_version = ldap.VERSION3
        ld.simple_bind_s(ldap_settings.LDAP_DOMAIN +
                         ldap_username, ldap_password)

        query = 'mail=' + username + '@*'
        ldap_objs = ld.search_s(LDAP_BASE_DN,
                                ldap.SCOPE_SUBTREE,
                                query,
                                None)

    except ldap.LDAPError as e:
        return {'error': str(e)}

    info = {}
    for dn, entries in ldap_objs:
        if (re.search(ldap_settings.INACTIVE_USER_STRING, dn) or
                re.search(ldap_settings.INVALID_USER_REGEX, dn)):
            continue
        info['cn'] = dn
        print "***** %s" % (dn)
        for key, val in entries.iteritems():
            if key == 'cn':
                continue
            elif key in ('displayName', 'mail'):
                info[key] = val[0]
            elif key == 'objectSid':
                info[key] = base64.b64encode(val[0])

    print "Got LDAP info:%s" % info
    if len(info) == 0:
        raise ldap.LDAPError("get_ldap_info error: "
                             "Unable to find info for %s" % username)

    return info


@transaction.autocommit
def get_authentication_cookie(user_info, service='go_url'):
    # check for collision (very unlikely)
    while True:
        auth_key = get_randomized_chars(64)
        try:
            models.SSOAuthInfo.objects.get(auth_key=auth_key)
        except models.SSOAuthInfo.DoesNotExist:
            # no collision, move on...
            break

    try:
        auth_obj = models.SSOAuthInfo(
            auth_key=auth_key,
            browser='',
            cn=user_info['cn'],
            displayName=user_info['displayName'],
            mail=user_info['mail'],
            objectSid=user_info['objectSid'],
            services=service,
            last_service=service)
    except DatabaseError as e:
        # pass, just store the error (could be "length too large", etc)
        transaction.rollback()
        raise e

    try:
        auth_obj.save()
    except IntegrityError as e:
        transaction.rollback()
        raise e

    return auth_key


@transaction.autocommit
def get_temporary_token(auth_key, service):
    """
    Transient token for applications.
    TODO(kevinx): 10 second or less active
    """
    # check for collision (very unlikely)
    while True:
        token = get_randomized_chars(48)
        try:
            models.SSOAppToken.objects.get(token=token)
        except models.SSOAppToken.DoesNotExist:
            break

    auth_obj = models.SSOAuthInfo.objects.get(auth_key=auth_key)

    try:
        #auth_obj.token_set.all()
        token_obj = auth_obj.ssoapptoken_set.create(token=token,
                                                    service=service)
    except DatabaseError as e:
        # pass, just store the error (could be "length too large", etc)
        transaction.rollback()
        raise e

    try:
        token_obj.save()
    except IntegrityError as e:
        transaction.rollback()
        raise e

    return token


def api_get_credentials_from_token(request, token):
    """
    API called by 3rd party services.
    """
    #token = request.GET.get('token', None)
    try:
        token_obj = models.SSOAppToken.objects.get(token=token)
    except models.SSOAppToken.DoesNotExist:
        token_obj = None

    if not token_obj:
        return HttpResponse("Token '%s' not found." % token)

    auth_obj = token_obj.ssoauthinfo
    # TODO(kevinx): uncomment in production
    #token_obj.delete()
    auth_info = {
        'cn': auth_obj.cn,
        'displayName': auth_obj.displayName,
        'mail': auth_obj.mail,
        'objectSid': auth_obj.objectSid
    }
    return HttpResponse(json.dumps(auth_info), content_type="text/plain")


def validate_cookie(request):
    """
    Check whether the user is logged in to SSO or not, and if so, forward
    to the appropriate service.
    """
    auth_key = request.COOKIES.get('auth_key', None)
    if not auth_key:
        # TODO(kevinx): add a prettier page
        return HttpResponse("Please enable cookie and "
                            "<a href=%s>try again</a>" %
                            custom_reverse_url('dsso:index'))

    # check that the cookie is valid
    try:
        models.SSOAuthInfo.objects.get(auth_key=auth_key)
    except models.SSOAuthInfo.DoesNotExist:
        # reset the cookie
        return HttpResponse("Unable to match your cookie."
                            "<a href=%s>Try again</a>" %
                            custom_reverse_url('dsso:index'))

    service = request.GET.get('service', None)
    if service in (VALID_SERVICES.keys()):
        token = get_temporary_token(auth_key, service)
        url = VALID_SERVICES[service]
        return HttpResponseRedirect('%s/validate_token/%s' % (url, token))

    return HttpResponseRedirect(custom_reverse_url('dsso:index'))


@transaction.autocommit
def signout(request):
    logout(request)
    response = HttpResponseRedirect(custom_reverse_url('dsso:index'))
    response.delete_cookie('auth_key')

    auth_key = request.COOKIES.get('auth_key', None)
    if auth_key:
        key_obj = models.SSOAuthInfo.objects.filter(auth_key=auth_key)
        if key_obj:
            key_obj.delete()

    return response
