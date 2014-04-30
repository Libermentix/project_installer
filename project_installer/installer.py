__author__ = 'Felix'
import os

import six
from unipath import Path

from jinja2 import Environment, FileSystemLoader

from .utils import logger

from .threads import Command, finish_queued_commands


class Installer(object):
    install_path = None
    postactivate = None
    postdeactivate = None

    project_name = None
    project_dir = None

    var_dict = {}

    post_run_command_stack = []


    def __init__(self, project_dir, project_name, envwrapper=False,
                 *args, **kwargs):
        self.project_dir = Path(project_dir).absolute()
        self.project_name = project_name
        self.is_envwrapper = envwrapper

        # make all attributes overridable so that external applications
        # can make use of the pattern and reset the variable names
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

        self.install_path = Path(self.project_dir, project_name)
        self.install_path.mkdir()
        self.install_path.chdir()

        self._environment_cache = False
        self._template_dir_cache = False
        self._template_cache = False

    @property
    def venv_folder(self):
        """
        extracts the venv folder from the environment variables ($WORKON_HOME,
        to be precise and combines it with the project name.
        """
        path = os.environ.copy().get('WORKON_HOME')
        if path:
            return Path(path)
        else:
            return None


    @property
    def template_env(self):
        """
        provides the template environment
        """
        if not getattr(self, '_environment_cache', False):
            self._environment_cache = Environment(
                loader=FileSystemLoader(self.get_template_dir())
            )

        return self._environment_cache

    def run_command(self, command, blocking=False):
        command = Command(command)

        command()

        if blocking:
            logger.debug('Waiting for command to finish...')
            command.wait()

        return True

    def finish_queued_commands(self):
        finish_queued_commands()

    def get_installer_name(self):
        return self.__class__.__name__.lower()

    def get_template_dir(self):
        if not getattr(self, '_template_cache', False):
            self._template_dir_cache = Path(Path(__file__).parent, 'templates')
        return self._template_dir_cache

    def get_template(self, which_one):
        """
        provides a wrapper around jinja2 get_template. Caches the result.
        returns a cached template
        """
        if not getattr(self, '_template_cache', False):
            self._template_cache = dict()

        if not self._template_cache.get(which_one, False):
            template_file = '%s.%s.sh' % (self.get_installer_name(), which_one)
            self._template_cache[which_one] = \
                self.template_env.get_template(template_file)

        return self._template_cache[which_one]

    def run_prepare_configuration(self):
        raise NotImplementedError('Must be implemented in subclass')

    def render_config_for_file_template(self, which_one):
        logger.info('preparing config variables for %s ...' % which_one)

        template = self.get_template(which_one=which_one)
        contents = template.render(**self.var_dict)

        setattr(self, '%s' % which_one, contents)

        logger.info('...done')

    def create_file(self, which_one):
        self.render_config_for_file_template(which_one=which_one)

        logger.info('Creating config files in parent dir: %s'
                    % self.install_path)

        #gets self.postdeactivate if which_one=postdeactivate
        contents = getattr(self, which_one)

        logger.info('%s: Writing contents to file ...' % which_one)

        p = Path(self.install_path, which_one)
        #write configuration and append it to the file
        p.write_file(contents, 'a+')
        logger.info('...done')

    def move_to_venv(self, which_one):
        """
        Moves the created config_files into the bin folder to be executed.
        Does this by first pasting all the contents of the temporary file
        into the new or existing target file and then deleting the temp file.
        """
        target = Path(self.venv_folder, self.project_name, 'bin', which_one)
        source = Path(self.install_path, which_one)
        logger.info('target: %s, move_orig: %s' % (target, source))

        if source.exists():
            logger.info('Moving %s into place ...' % which_one)
            content = source.read_file()

            #make sure the directory exists
            if not target.parent.exists():
                target.parent.mkdir(parents=True)
            target.write_file(content, 'w+')

            source.remove()

        logger.info('...done')

    def run_create_configuration(self):
        self.create_file(which_one='postactivate')
        self.create_file(which_one='postdeactivate')

    def run_post_create_configuration(self):
        pass

    def run(self):
        self.run_prepare_configuration()
        self.run_create_configuration()
        self.run_post_create_configuration()

    def __call__(self, *args, **kwargs):
        self.run()












