from os import environ as current_env
from threading import Thread
from Queue import Queue, Empty
from subprocess import Popen, PIPE
from tempfile import SpooledTemporaryFile

import shlex
import atexit

from .utils import logger

queue = Queue(40)
processes = list()
producers = list()
consumer = None

##
## Based on a tutorial:
## http://agiliq.com/blog/2013/10/producer-consumer-problem-in-python/
## threading and Popen:
## http://sharats.me/the-ever-useful-and-neat-subprocess-module.html
##

class ProducerThread(Thread):
    def __init__(self, stream):
        self.stream = stream
        super(ProducerThread, self).__init__()

    def run(self):
        global queue

        # http://blog.amir.rachum.com/blog/2013/11/10/
        # python-tips-iterate-with-a-sentinel-value/#fn:1
        for line in iter(self.stream.readline, ''):
            queue.put(line)


class ConsumerThread(Thread):
    def __init__(self):
        super(ConsumerThread, self).__init__()

    def run(self):
        global queue
        global processes

        while True:
            try:
                result = queue.get(timeout=1)
            except Empty:
                if len(processes) < 1:
                    logger.debug('All processes ended successfully')
                    break

                for proc in processes:
                    if proc.poll() is not None:
                        #remove process from the stack
                        processes.remove(proc)
                        logger.debug('%s: ended sucessfully' % proc.pid)
            else:
                print(result)


def finish_queued_commands():
    global producers
    logger.debug('Finishing queued threads and processes ...')
    for thread in producers:
        thread.join()
    logger.debug('All queued threads finished')

    for proc in processes:
        proc.wait()
    logger.debug('All queued process finished')

    logger.debug('Finishing up the producer as well....')
    consumer.join()

    logger.debug('...done')


class Command(object):
    proc = None
    command = None

    def __init__(self, command):

        if isinstance(command, basestring):
            command = shlex.split(command)

        assert isinstance(command, list), 'command must be of type list ' \
                                          'or basestring not %s' % type(command)

        self.command = command

    def __call__(self):
        self.run_command()

    def wait(self):
        self.proc.wait()

    def run_command(self):
        global processes
        global producers
        global consumer

        self.proc = Popen(
            self.command,
            shell=False,
            stdout=PIPE,
            stderr=PIPE,
            env=current_env.copy()
        )

        processes.append(self.proc)

        stdout = ProducerThread(stream=self.proc.stdout)
        stderr = ProducerThread(stream=self.proc.stderr)

        producers.append(stdout)
        producers.append(stderr)

        stdout.start()
        stderr.start()

        if len(processes) == 1:
            # start the consumer thread only once there are actual processes
            # to listen to.
            consumer = ConsumerThread()
            consumer.start()


@atexit.register
def kill_all_process():
    for proc in processes:
        proc.kill()



