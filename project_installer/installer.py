__author__ = 'Felix'
import os

import six
from unipath import Path
from jinja2 import Template

from .utils import logger


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
    def template_folder(self):
        """
        provides the template folder
        """
        return Path((__file__).parent,'templates')

    def get_template(self, which_one):
        installer_name = Path(__file__).stem
        template_file = Path(
            self.template_folder, installer_name, '.' , which_one, '.sh'
        )
        return template_file

    def run_prepare_configuration(self):
        raise NotImplementedError('Must be implemented in subclass')

    def prepare_config_for_file_creation(self, which_one):
        logger.info('preparing config variables ...')
        if not getattr(self, which_one):
            raise NotImplementedError('Postactivate needs to be set.')

        contents = Template(
            self.get_template(which_one=which_one)
        ).render(**self.var_dict)

        setattr(self, '%s' % which_one, contents)

        logger.info(contents)

    def create_file(self, which_one):
        self.prepare_config_for_file_creation(which_one=which_one)

        logger.info('Creating config files in parent dir: %s'
                    % self.install_path)

        #gets self.postdeactivate if which_one=postdeactivate
        contents = getattr(self, which_one)

        logger.info('%s: Writing contents to file ...' % which_one)

        p = Path(self.install_path, which_one)
        #write configuration and append it to the file
        p.write_file(contents, 'a+')
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











