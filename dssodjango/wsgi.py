from django.core.wsgi import get_wsgi_application
import os
#from django.core.handlers.wsgi import WSGIHandler


# this is required even though __init__.py already defined it
os.environ['DJANGO_SETTINGS_MODULE'] = 'dssodjango.settings'

#application = WSGIHandler()
application = get_wsgi_application()
