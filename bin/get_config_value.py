#!/usr/bin/python2.7
"""
Common Python configurations.
"""
import os
import sys

#try:
#    from dcommon import PROJECT_PATH, get_config_value
#except ImportError:
    # this is run from the bin/ directory, thus the context of
    # dcommon is lost at the start of this program.
#    ppath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "..")
#    sys.path.append(ppath)
#    from dcommon import PROJECT_PATH, get_config_value
from configs.common import PROJECT_PATH, get_config_value

DATA_PATH = os.path.join(PROJECT_PATH, 'data')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Please specify a configuration name")
    print get_config_value(sys.argv[1], PROJECT_PATH)
