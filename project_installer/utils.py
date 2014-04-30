__author__ = 'Felix'
import logging

import os
import string
import random

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger('project_installer.logger')


class ImproperlyConfigured(ValueError):
    pass

characterset = string.ascii_letters+string.digits+'_!,.<>/?;:'


def generate_unique_id(length=6, chars=characterset):
    '''
    generates an id of length picked out of chosen characters
    see: http://stackoverflow.com/questions/2257441/
    python-random-string-generation-with-upper-case-letters-and-digits
    '''
    return u''.join(random.choice(chars) for _ in range(length))


def get_env_variable(var_name):
    msg = 'Set the %s environment variable'
    try:
        return os.environ[var_name]
    except:
        error_msg = msg % var_name
        raise ImproperlyConfigured(error_msg)


def add_trailing_slash(target_string):
    return target_string if target_string[-1:]=='/' else target_string+'/'
