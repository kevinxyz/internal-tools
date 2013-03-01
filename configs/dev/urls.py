# Make sure that /etc/hosts are sync'ed to the development VM.
# Sync this with common_utils.py/reverse_url(...)

# Map between a service name to URL
import os
import re

if 'DJANGO_STANDALONE_SERVER' in os.environ:
    # local debugging using Django's manage.py (without nginx):
    URL = 'http://172.16.238.88:7000'
    SERVICE_TO_URL = {
        'sample_app': URL + '/sample_app',
        'dsso': URL + '/dsso',
        'go_url': URL + '/go_url',
        'who': URL + '/who',
        'better360': URL + '/better360',
        'roulette': URL + '/roulette',
    }
    ROULETTE_SERVER = re.sub('7000', '8888', URL)
else:
    # Run with nginx, with URLs remapped
    URL = 'http://qa-labs'
    SERVICE_TO_URL = {
        'sample_app': URL + '/sample_app',
        'dsso': 'http://qa-dsso',
        'go_url': 'http://qa-go',
        'who': 'http://qa-who',
        'better360': URL + '/better360',
        'roulette': URL + '/roulette',
    }
    ROULETTE_SERVER = URL + ':8888'
