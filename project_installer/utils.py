__author__ = 'Felix'
import logging

import os
import string
import random
from Queue import Queue, Empty

class ImproperlyConfigured(ValueError):
    pass

def generate_unique_id(length=6, chars=string.ascii_uppercase+string.digits):
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




#threading and Popen: http://sharats.me/the-ever-useful-and-neat-subprocess-module.html

io_q = Queue()

def stream_watcher(identifier, stream):

    for line in stream:
        io_q.put((identifier, line))

    if not stream.closed:
        stream.close()


def printer(proc):
    while True:
        try:
            # Block for 1 second.
            item = io_q.get(True, 1)
        except Empty:
            # No output in either streams for a second. Are we done?
            if proc.poll() is not None:
                break
        else:
            identifier, line = item
            print identifier + ':', line