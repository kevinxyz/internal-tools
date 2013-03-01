# coding=utf-8
from copy import copy
import json
import re

from django.db.models import F, Max, Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

from configs.settings import who as who_settings
from configs.settings import constants
from configs.settings.ldap import INACTIVE_USER_STRING, CONTRACTOR_STRING

from dssodjango.common_utils import (
    add_query_parameter,
    app_validate_token, app_validate_cookie, app_signout,
    get_app_credentials_from_auth_value, custom_reverse_url,
    SSO_URL, get_app_urls)
from dssodjango.models import LDAPUser

APP_NAME = 'who'
APP_AUTH_KEY = 'app_auth_key'


def validate_token(request, token):
    return app_validate_token(request, token, APP_AUTH_KEY,
                              custom_reverse_url(APP_NAME + ':validate_cookie'))


def validate_cookie(request):
    return app_validate_cookie(request, APP_AUTH_KEY,
                               custom_reverse_url(APP_NAME + ':index'))


def signout(request):
    return app_signout(request, APP_AUTH_KEY)


def get_js_hierarchy(request,
                     who_url,
                     obj_self,
                     obj_parent,
                     level=2,
                     obj_visited=set(),
                     show_inactive_user=False):
    """
    Recursively go through obj_self...
    """
    relationships = []  # used by the Google JavaScript
    ldap_objects = []

    if level <= 0 or obj_self in obj_visited:
        return relationships, ldap_objects

    if not show_inactive_user and not obj_self.is_active:
        # if flag is to not show inactive and user is not active, skip
        return relationships, ldap_objects

    ldap_obj_dict = obj_self.__dict__
    ldap_obj_dict['username'] = obj_self.username
    ldap_obj_dict['photo_url'] = obj_self.photo_url
    _template = TemplateResponse(request,
                                 APP_NAME + '/person.html',
                                 {'ldap_obj': ldap_obj_dict,
                                  'who_url': who_url})
    _template.render()
    relationships.append(({
                              'v': obj_self.mail,
                              'f': _template.content
                          },
                          obj_parent.mail if obj_parent else '',
                          obj_self.mail))
    ldap_objects.append(obj_self)
    obj_visited.add(obj_self)

    for report_obj in obj_self.reports:
        _relationship, _ldap_objects = get_js_hierarchy(request,
                                                        who_url,
                                                        report_obj,
                                                        obj_self,
                                                        level - 1,
                                                        obj_visited,
                                                        show_inactive_user)
        relationships.extend(_relationship)
        ldap_objects.extend(_ldap_objects)
    return relationships, ldap_objects


def get_data_properties(self_ldap_object, ldap_objects):
    properties = []
    for idx, ldap_object in enumerate(ldap_objects):
        if not ldap_object.is_active:
            properties.append((idx, 'style', 'background-color: gray'))
        elif ldap_object == self_ldap_object:
            properties.append((idx, 'style', 'background-color: #33CCFF'))
    return properties


def get_object_by_query(query, show_inactive_user=False):
    def _safe_query(func):
        try:
            ldap_objs = func()
            if not show_inactive_user:
                ldap_objs = [obj for obj in ldap_objs if obj.is_active]
            if ldap_objs and len(ldap_objs) > 0:
                return ldap_objs
        except LDAPUser.DoesNotExist:
            pass
        return []

    def _alias_query_func(query):
        q = (Q(mail__icontains=query) | Q(displayName__icontains=query) |
             Q(department__icontains=query) | Q(title__icontains=query))
        for same_names in who_settings.ALIASES:
            if query in same_names:
                for alt_name in [n for n in same_names if n != query]:
                    print "ALIAS of %s:%s" % (query, alt_name)
                    q |= (Q(mail__icontains=alt_name) |
                          Q(displayName__icontains=alt_name))
            continue
        return LDAPUser.objects.filter(q)

    ldap_objs = None
    for query_func in (
        lambda :LDAPUser.objects.filter(
                Q(mail__iexact=query) | Q(displayName__iexact=query)),
        lambda :_alias_query_func(query),
        lambda :LDAPUser.objects.filter(
                cn__icontains=re.sub(' ', '.', query))
    ):
        ldap_objs = _safe_query(query_func)
        if ldap_objs:
            break

    # corner case: two same identities, but only one is active!
    if len(ldap_objs) > 1:
        same_email = True
        first_mail = ldap_objs[0].mail
        for _email in [obj.mail for obj in ldap_objs[1:]]:
            if _email != first_mail:
                same_email = False
                break
        if same_email:
            ldap_objs = [obj for obj in ldap_objs if obj.is_active]

    return ldap_objs


def get_employee_ranking(ldap_obj,
                         departments=None,
                         titles=None,
                         include_contractors=False,
                         include_inactives=False,):
    hire_date = ldap_obj.hire_date
    if not hire_date:
        return None, None

    youngens = LDAPUser.objects.filter(hire_date__gt=hire_date)
    oldfarts = LDAPUser.objects.filter(hire_date__lt=hire_date)

    if not include_inactives:
        youngens = youngens.filter(~Q(cn__icontains=INACTIVE_USER_STRING))
        oldfarts = oldfarts.filter(~Q(cn__icontains=INACTIVE_USER_STRING))

    if departments:
        for department in departments.split(' AND '):
            youngens = youngens.filter(Q(department__icontains=department))
            oldfarts = oldfarts.filter(Q(department__icontains=department))

    if titles:
        for title in titles.split(' AND '):
            youngens = youngens.filter(Q(title__icontains=title))
            oldfarts = oldfarts.filter(Q(title__icontains=title))

    if not include_contractors:
        youngens = youngens.filter(~Q(cn__icontains=CONTRACTOR_STRING))
        oldfarts = oldfarts.filter(~Q(cn__icontains=CONTRACTOR_STRING))

    youngens = sorted(youngens, key=lambda x: x.hire_date, reverse=False)
    oldfarts = sorted(oldfarts, key=lambda x: x.hire_date, reverse=True)

    def set_contract_and_active_states(ldap_objs):
        for ldap_obj in ldap_objs:
            if re.search(INACTIVE_USER_STRING, ldap_obj.cn):
                ldap_obj.inactive = True
            if re.search(CONTRACTOR_STRING, ldap_obj.cn):
                ldap_obj.contractor = True
        return ldap_objs

    #youngens = set_contract_and_active_states(youngens)
    #oldfarts = set_contract_and_active_states(oldfarts)

    return youngens, oldfarts


def percentpost(request):
    """
    POST to URL forwarder (preserves the query)
    """
    url = custom_reverse_url(APP_NAME + ':percent')
    for param in ('departments', 'titles', 'contractors', 'inactives'):
        value = request.POST.get(param, None)
        if value:
            url = add_query_parameter(url, param, value)

    return HttpResponseRedirect(url)


def percent(request):
    cn, _, email, _, _ = get_app_credentials_from_auth_value(
        request.COOKIES.get(APP_AUTH_KEY, None))

    who_url = custom_reverse_url(APP_NAME + ':index')
    percentpost_url = custom_reverse_url(APP_NAME + ':percentpost')

    if not email:
        return HttpResponseRedirect(who_url)

    ldap_objs = get_object_by_query(email, show_inactive_user=False)
    if len(ldap_objs) != 1:
        return HttpResponse("Error, unable to find a unique person "
                            "for '%s'" % email)
    ldap_obj = ldap_objs[0]

    departments = request.GET.get('departments', '')
    titles = request.GET.get('titles', '')
    include_contractors = request.GET.get('contractors', '')
    include_inactives = request.GET.get('inactives', '')

    # calculate seniority
    youngens1, oldfarts1 = get_employee_ranking(
        ldap_obj,
        include_contractors=False,
        include_inactives=False)
    youngens2, oldfarts2 = get_employee_ranking(
        ldap_obj,
        departments=departments,
        titles=titles,
        include_contractors=include_contractors,
        include_inactives=include_inactives)
    #print "HEY %s / %s" % (oldfarts.count(), youngens.count())

    total_queried_employees = (len(youngens1) + len(oldfarts1))
    percentile1 = ((float(len(youngens1)) / total_queried_employees)
                   if total_queried_employees > 0 else 0)
    percentile1 *= 100

    total_queried_employees = (len(youngens2) + len(oldfarts2))
    percentile2 = ((float(len(youngens2)) / total_queried_employees)
                   if total_queried_employees > 0 else 0)
    percentile2 *= 100

    def add_date_attribute(ldap_objs):
        for ldap_obj in ldap_objs:
            ldap_obj.hire_date = ldap_obj.hire_date.strftime("%Y-%m-%d")
        return ldap_objs

    context = {
        'who_url': who_url,
        'percentpost_url': percentpost_url,
        'email': email,
        'displayName': ldap_obj.displayName,
        'company_employee_name': constants.COMPANY_EMPLOYEE_NAME,
        'signin_url': add_query_parameter(SSO_URL, 'service', APP_NAME),
        'signout_url': custom_reverse_url(APP_NAME + ':signout'),
        'app_urls': get_app_urls(),

        # form for query ranking
        'departments': departments,
        'titles': titles,
        'include_contractors': include_contractors,
        'include_inactives': include_inactives,

        # display objects
        'hire_date': ldap_obj.hire_date,
        'company_percentile': percentile1,
        'company_youngens': add_date_attribute(youngens1),
        'company_oldfarts': add_date_attribute(oldfarts1),
        'specific_percentile': percentile2,
        'specific_youngens': add_date_attribute(youngens2),
        'specific_oldfarts': add_date_attribute(oldfarts2),
    }
    #print "%s %s"%(youngens2[0].hire_date, type(youngens2[0].hire_date))
    #print "%s" % youngens2[0].hire_date.strftime("%Y-%m-%d")
    return render_to_response(APP_NAME + '/percent.html',
                              context,
                              context_instance=RequestContext(request))


def index(request, query=None):
    """
    Main entrance page.
    """
    post_query = request.POST.get('query')
    if post_query:
        return HttpResponseRedirect(
            custom_reverse_url(APP_NAME + ':index') + post_query)

    cn, _, email, displayName, _ = get_app_credentials_from_auth_value(
        request.COOKIES.get(APP_AUTH_KEY, None))

    if email:
        show_inactive_user = True
    else:
        show_inactive_user = False

    extra_hierarchy_levels = 0
    if not query:
        if email:
            ldap_objs = get_object_by_query(email, show_inactive_user)
        else:
            ldap_objs = get_object_by_query(who_settings.BOSS,
                                            show_inactive_user)
    else:
        while query.endswith('+'):
            query = query[:-1]
            extra_hierarchy_levels += 1
        ldap_objs = get_object_by_query(query, show_inactive_user)

    who_url = custom_reverse_url(APP_NAME + ':index')

    possible_objs = []
    json_relationships = None
    data_properties = None
    chart_size = None

    if len(ldap_objs) > 1:
        possible_objs = ldap_objs

    elif len(ldap_objs) == 1:
        ldap_obj = ldap_objs[0]

        manager_obj = LDAPUser.objects.get(id=ldap_obj.manager_id)
        sibling_obj_set = set()
        if ldap_obj == manager_obj:
            # big boss
            pass
        else:
            for _obj in manager_obj.reports:
                if _obj != ldap_obj and _obj != manager_obj:
                    # 1) skip the report right under manager
                    sibling_obj_set.add(_obj)

        # recursive call, potentially slow:
        relationships, ldap_objects = get_js_hierarchy(
            request,
            who_url,
            manager_obj,
            None,
            3 + extra_hierarchy_levels,
            copy(sibling_obj_set),
            show_inactive_user)

        json_relationships = json.dumps(relationships)
        print "Json relationships:%s" % json_relationships

        data_properties = get_data_properties(ldap_obj, ldap_objects)
        print "Styling:%s" % data_properties

        #chart_size = ('large' if len(relationships) <= 6 else
        #              'medium' if len(relationships) <= 12 else 'small')
        chart_size = 'medium'

    context = {
        'who_url': who_url,
        'email': email,
        'displayName': displayName,
        'company_employee_name': constants.COMPANY_EMPLOYEE_NAME,
        'query': query or '',
        'extra_hierarchy_header': '+' * (extra_hierarchy_levels + 1),
        'signin_url': add_query_parameter(SSO_URL, 'service', APP_NAME),
        'signout_url': custom_reverse_url(APP_NAME + ':signout'),
        'percent_url': custom_reverse_url(APP_NAME + ':percent'),
        'app_urls': get_app_urls(),
        # ambiguous query, list choices
        'possible_objs': possible_objs,
        # for graphing:
        'json_relationships': json_relationships,
        'data_properties': data_properties,
        'chart_size': chart_size,
    }
    return render_to_response(APP_NAME + '/index.html',
                              context,
                              context_instance=RequestContext(request))
