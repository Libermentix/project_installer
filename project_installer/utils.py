__author__ = 'Felix'
import logging

import os
import string
import random
from Queue import Queue, Empty
from threading import Thread
from subprocess import Popen, PIPE

logger = logging.getLogger('project_installer.logger')
logger.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
)


class ImproperlyConfigured(ValueError):
    pass

characterset = string.ascii_letters+string.digits+'_)(*&^%$#@!,.<>/?;:'

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
            if identifier == 'err':
                logger.error(line)
            else:
                logger.info(line)


def run_command(command):
    proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

    Thread(target=stream_watcher, name='stdout-watcher',
            args=('out', proc.stdout)).start()
    Thread(target=stream_watcher, name='stderr-watcher',
            args=('err', proc.stderr)).start()
    Thread(target=printer, args=(proc,),name='printer').start()