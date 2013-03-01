# Debug logging on development machine
import logging
import os

LEVEL = (getattr(logging, os.environ['DEBUG']) if 'DEBUG' in os.environ
         else logging.DEBUG)
