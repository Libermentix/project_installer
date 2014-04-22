__author__ = 'Felix'
import logging
import os
import six

from unipath import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class Installer(object):
    install_path = Path().absolute()
    postactivate = None
    postdeactivate = None

    project_name = None
    project_dir = None

    def __init__(self, project_dir, project_name, envwrapper=False,
                 *args, **kwargs):
        self.project_dir = project_dir
        self.project_name = project_name
        self.is_envwrapper = envwrapper

        # make all attributes overridable so that external applications
        # can make use of the pattern and reset the variable names
        for k, v in six.iteritems(kwargs):
            setattr(self, key=k, value=v)


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

    def run_commands(self):
        raise NotImplementedError('Must be implemented in subclass')

    def create_postactivate(self):
        logging.info('Creating postactivate script')

        if not self.postactivate:
            raise NotImplementedError('Postactivate needs to be set')

        self.postactivate = self.postactivate % self.var_dict
        logging.info (self.postactivate)

    def create_postdeactivate(self):
        logging.info('Creating postdeactivate script')

        if not self.postdeactivate:
            raise NotImplementedError('Postdeactivate needs to be set')

        self.postdeactivate = self.postdeactivate % self.var_dict
        logging.info(self.postdeactivate)

    def create_config(self, which_one):
        create_func= getattr(self, 'create_%s' % which_one)
        create_func()

    def create_file(self, which_one):
        self.create_config(which_one=which_one)

        logging.info('Creating config files in parent dir: %s'
                     % self.install_path)

        #gets self.postdeactivate if which_one=postdeactivate
        contents = getattr(self, which_one)

        logging.info('%s: Writing contents to file: \n %s'
                     % (which_one, contents)
        )

        p = Path(self.install_path, which_one)
        #write configuration and append it to the file
        p.write_file(contents, 'a+')
        logging.info('...done')

    def run_create_config_files(self):
        self.create_file(which_one='postactivate')
        self.create_file(which_one='postdeactivate')

    def run(self):
        self.run_commands()
        self.run_create_config_files()

    def __call__(self, *args, **kwargs):
        self.run()











