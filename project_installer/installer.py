__author__ = 'Felix'
import logging
import os
import six

from unipath import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

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

    def run_prepare_configuration(self):
        raise NotImplementedError('Must be implemented in subclass')

    #def create_postactivate(self):
    #    logging.info('Creating postactivate script')
    #
    #    if not self.postactivate:
    #        raise NotImplementedError('Postactivate needs to be set')

    #    self.postactivate = self.postactivate % self.var_dict

    #def create_postdeactivate(self):
    #    logging.info('Creating postdeactivate script')#
    #
    #    if not self.postdeactivate:
    #        raise NotImplementedError('Postdeactivate needs to be set')
    #
    #    self.postdeactivate = self.postdeactivate % self.var_dict

    def prepare_config_for_file_creation(self, which_one):
        logging.info('preparing config variables ...')
        if not getattr(self, which_one):
            raise NotImplementedError('Postactivate needs to be set.')

        setattr(self, which_one, which_one % self.var_dict)

        logging.info(getattr(which_one))

    def create_file(self, which_one):
        self.prepare_config_for_file_creation(which_one=which_one)

        logging.info('Creating config files in parent dir: %s'
                     % self.install_path)

        #gets self.postdeactivate if which_one=postdeactivate
        contents = getattr(self, which_one)

        logging.info('%s: Writing contents to file ...' % which_one)

        p = Path(self.install_path, which_one)
        #write configuration and append it to the file
        p.write_file(contents, 'a+')
        logging.info('...done')

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











