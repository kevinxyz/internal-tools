#!/usr/bin/python2.7
"""
Common Python configurations.
"""
import imp
import os
import sys

# Do *NOT* put any Django dependencies here, otherwise Django will
# see circular dependencies and start to print weird messages:
#try:
#    from dcommon import PROJECT_PATH, get_config_value
#except ImportError:
    # this is run from the bin/ directory, thus the context of
    # dcommon is lost at the start of this program.
#    ppath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "..")
#    sys.path.append(ppath)
#    from dcommon import PROJECT_PATH, get_config_value

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(
    sys.modules[__name__].__file__), ".."))

DATA_PATH = os.path.join(PROJECT_PATH, 'data')


def get_environment_name(project_path):
    """
    Get the current environment name (and do basic environment check).
    """
    if not os.path.exists(project_path):
        raise RuntimeError("Unable to find project path '%s'" % project_path)

    environment_name = os.environ.get('PROJECT_ENV', None)
    if not environment_name:
        raise RuntimeError("Please specify a PROJECT_ENV in the environment")

    return environment_name


def get_config_value(name, project_path=PROJECT_PATH):
    """
    Find configuration and return the value
    """
    environment_name = get_environment_name(project_path)

    if '.' in name:
        # if there is an entry like storage.PG_USER, then:
        # config_path will use storage.py
        # name will be PG_USER
        config_path = os.path.join(project_path,
                                   'configs',
                                   environment_name,
                                   *name.split('.')[:-1])
        name = name.split('.')[-1]
    else:
        config_path = os.path.join(project_path, 'configs', 'common')

    config_file = config_path + '.py'
    if not os.path.exists(config_file):
        raise RuntimeError("Unable to find config file '%s'" % config_file)

    settings = imp.load_source('', config_file)
    if not hasattr(settings, name):
        raise RuntimeError("Unable to find '%s', try:%s" %
                           (name, dir(settings)))
    return getattr(settings, name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Please specify a configuration name")
    print get_config_value(sys.argv[1], PROJECT_PATH)
