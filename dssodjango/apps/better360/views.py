# coding=utf-8
import random
import re

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from configs.settings.constants import (
    COMPANY_NICKNAME, COMPANY_EMPLOYEE_NAME, COMPANY_NAME)


from dssodjango.common_utils import (
    add_query_parameter,
    app_validate_token, app_validate_cookie, app_signout,
    get_app_credentials_from_auth_value, custom_reverse_url,
    SSO_URL, get_app_urls)

APP_NAME = 'better360'
APP_AUTH_KEY = 'app_auth_key'


def validate_token(request, token):
    return app_validate_token(request, token, APP_AUTH_KEY,
                              custom_reverse_url(APP_NAME + ':validate_cookie'))


def validate_cookie(request):
    return app_validate_cookie(request, APP_AUTH_KEY,
                               custom_reverse_url(APP_NAME + ':index'))


def signout(request):
    return app_signout(request, APP_AUTH_KEY)



## Below are from Dilbert's performance generator
def get_dilbert_perf(
        person_name, project_name,
        knowledge, initiative, dependability,
        adaptability, quality, quantity):
    ## Below are from Dilbert's performance generator

    _buf = []

    # Score knowledge
    knowledge_text = (
        "You see $personName and like the bums in UCLA you don't really remember his name.",
        "$personName does the kind of work you don't expect to see today and he handles assignments with unlooked-for creativity.", 
        "$personName's worth to the company can only be imagined.", 
        "$personName leaves quite an impression on the division. He is like Third Street Promenade, always busy and never stopping.",
        "$personName has name recognition throughout the divisions. He shines in the group, and working with him is like sun-bathing on the amazing Santa Monica beach.")
    _buf.append(knowledge_text[knowledge])

    knowledge_text = (
        "$personName learns slowly, and seems like a newbie.",
        "$personName could possible go back to school to re-learn some of the important materials.",
        "$personName works very hard like an average worker.",
        "$personName is pretty good technically.",
        "$personName has a complete mastery of technologies.")
    _buf.append(knowledge_text[knowledge])

    # Random
    _buf.append(random.choice((
        "Quite an impressionable $companyEmployeeNickname, yeah...",
        "He is the embodiment of $companyEmployeeNickname.",
        "Gets along with other $companyEmployeeNickname.",
        "Has leadership skills, especially with New$companyEmployeeNickname.",
        "A member in the best company in the world-- $companyName.")))

    quantity_text = (
        "He does work on somewhat related materials, and the amount of result could be improved.",
        "Sometimes he could be using his time more efficiently, but otherwise a valuable employee to have.",
        "He is a decent worker and accomplishes tasks on time. He is quite an asset to the company.",
        "He is very efficient and does not waste any time.",
        "The rate of progress is astonishing and the company cannot survive without him.")
    _buf.append(quantity_text[quantity])

    quality_text = (
        "The quality needs more work. Going back to school or getting more experience may be a good idea.",
        "Sometimes the work could be improved upon, but it is the attempt that matters.",
        "His objectives are always reached and satisfactory.",
        "The results are consistently impressive.",
        "The quality of his work is unparalleled.")
    _buf.append(quality_text[quality])

    initiative_text = (
        # Score initiative
        "Like Panda, destroys other people's initiatives",
        "Makes little or no effort to engage in productive activities even while making no pretense of criticising to management.",
        "Makes little or no effort to engage in counterrevolutionary activities even while making no pretense of being open to criticism from management.",
        "Quite a Panda killer. Love it!",
        "Projected employee growth strategy compelled them to perform above the standard for this position even while making no pretense of being open to criticism from management.")
    _buf.append(initiative_text[initiative])

    initiative_text = (
        "$personName performs adaquately when given a specic task to do.",
        "$personName is a very good worker. Can follow instructions very well.",
        "A self motivator, an innovator, and does not need to be told what to do.",
        "A manager material, someone who initiates and creates great waves.",
        "Does not need anyone to tell him what to do. He always finds new and interesting problems to work on.")
    _buf.append(initiative_text[initiative])

        # Random:
    _buf.append(random.choice((
        "Internal success plan required them to team-build and involve others in problem-solving exceeding prior goal levels suggested by simian appearance.",
        "He prefers to work under minimal supervision and he makes decisions with minimal direction.",
        "Her future with this company is not in doubt.",
        "The quality of his work is well known.",
        "Additionally, he actively pursues relationships with his coworkers.")))
        
        # Random:
    _buf.append(random.choice((
        "He has worked on $projectName.",
        "He has extensive knowledge on $projectName.",
        "$projectName is his specialty.",
        "The knowledge he has on $projectName is extensive.")))

    adaptability_text = (
        "Adapts to new problems very steadily; sometimes slowly but always surely.",
        "Does adequate work load and is unique, like everyone else.",
        "He is a great employee; copes and solves new problems at a very good rate.",
        "He is like a genius; copes and solves new problems with ease.",
        "His adaptability is amazing; absorbs information and makes astonishing changes to the products.")
    _buf.append(adaptability_text[adaptability])

        # Random:
    _buf.append(random.choice((
        "He appears ever productive and has been seen dropping in at off hours.",
        "The quality of his work is well known.",
        "Not surprisingly, her usefulness to the division is self evident.",
        "His work may greatly impact the company and a thorough analysis of his performance will surprise you.",
        "Internal success plan required them to expand knowledge base to company advantage despite repeated attempts by management to intervene.")))
        
        # Score dependability
    dependability_text = (
        "Flakey as hell, damnit.",
        "Barring the unfortunate incident, reliably will attack problem-solving using more unique strategies regardless of the complete absence of support staff.",
        "Could be relied upon to team-build and involve others in problem-solving regardless of the complete absence of support staff.",
        "Has been expected to team-build and involve others in problem-solving despite repeated attempts by management to intervene.",
        "Routinely will engage in beneficial, proactive work strategies.")
    _buf.append(dependability_text[dependability])

        # Random:
    _buf.append(random.choice((
        "His 'capabilities' have only been recently discovered and such an employee demonstrates the importance of proper recruiting.",
        "His core values show through in his work and he has a wide variety of interests and pursuits.",
        "$personName works behind the scenes.",
        "He is not afraid to ask questions that check the assumptions of others.",
        "His performance defies measurement.")))
        
        # Random:
    _buf.append(random.choice((
        "$personName handles assignments with unlooked-for creativity and his usefulness to the division is self evident.",
        "It would be accurate to say that his work may greatly impact the company.",
        "I find that $personName is willing to take risks.",
        "The record should state that a reevaluation of his salary is long overdue.")))
        
        # Random:
    _buf.append(random.choice((
        "It's tough for management to keep up with him.",
        "One can not say enough 'things' about him.",
        "Definitely shows potential for unbounded improvement.",
        "Routinely will perform above the standard for this position while opening new markets for the company by developing offshore corporate alter-ego entities.",
        "Has been expected to placate or excuse previously noted behavior issues resulting in superior department performance.")))
        
        # Random:
    _buf.append(random.choice((
        "Moreover, his usefulness to the division is self evident and one can not say enough things about him.",
        "His name is frequently mentioned in executive meetings.",
        "A reevaluation of his assignments may be in order."
        )))

    _buffer = []
    for line in _buf:
        line = re.sub(r'\$personName', person_name, line)
        line = re.sub(r'\$projectName', project_name, line)
        line = re.sub(r'\$companyName', COMPANY_NAME, line)
        line = re.sub(r'\$companyNickname', COMPANY_NICKNAME, line)
        line = re.sub(r'\$companyEmployeeName', COMPANY_EMPLOYEE_NAME, line)
        _buffer.append(line)

    return _buffer


def index(request):
    """
    Main entrance page.
    """
    _, username, email, displayName, _ = get_app_credentials_from_auth_value(
        request.COOKIES.get(APP_AUTH_KEY, None))

    signin_url = add_query_parameter(SSO_URL, 'service', APP_NAME)
    context = {
        'email': email,
        'displayName': displayName,
        'signin_url': signin_url,
        'signout_url': custom_reverse_url(APP_NAME + ':signout'),
        'better360_url': custom_reverse_url(APP_NAME + ':index'),
        'app_urls': get_app_urls(),
        'content': None
    }

    if not email:
        return HttpResponseRedirect(signin_url)

    person_name = request.REQUEST.get('personName')
    project_name = request.REQUEST.get('projectName')
    if person_name and project_name:
        context['content'] = get_dilbert_perf(
            person_name,
            project_name,
            int(request.REQUEST.get('knowledge')) - 1,
            int(request.REQUEST.get('initiative')) - 1,
            int(request.REQUEST.get('dependability')) - 1,
            int(request.REQUEST.get('adaptability')) - 1,
            int(request.REQUEST.get('quality')) - 1,
            int(request.REQUEST.get('quantity')) - 1
            )
        context['content'] = ' '.join(context['content'])
        context['person_name'] = person_name
        context['project_name'] = project_name

    return render_to_response(APP_NAME + '/index.html',
                              context,
                              context_instance=RequestContext(request))
