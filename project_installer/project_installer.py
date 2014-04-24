__author__ = 'Felix'
from unipath import Path
import git

from .installer import Installer
from .database_installer import DatabaseInstaller
from .django_installer import DjangoInstaller
from .utils import run_command, logger


class ProjectInstaller(Installer):
    postactivate = '''#!/bin/bash
                   #setting project related variables
                   export PROJECT_NAME="%(project_name)s
                   export PROJECT_PATH="%(project_dir)s"
                   echo "virtual environment for application in project path: $PROJECT_PATH"
                   #extend python path
                   EXTENSION=""
                   if [ -n "$PYTHONPATH" ] ; then
                        OLD_PYTHON_PATH="$PYTHONPATH"
                        export OLD_PYTHON_PATH
                        EXTENSION=":${OLD_PYTHON_PATH}"
                   fi
                   export PYTHONPATH=${PROJECT_PATH}${EXTENSION}

                   '''

    postdeactivate = '''
                     #unsetting project related variables
                     unset PROJECT_BASE_PATH
                     unset PROJECT_NAME
                     unset PROJECT_PATH
                     export PYTHONPATH=${OLD_PYTHON_PATH}

                     '''

    flavor = 'django_custom'
    git_repo = 'https://github.com/Libermentix/venv_skeletton_directory.git'

    def __init__(self, project_dir, project_name,
                 db_sudo=False, db_sudo_user=None, *args, **kwargs):
        super(ProjectInstaller, self).__init__(
            project_dir, project_name, *args, **kwargs
        )
        self.var_dict = dict(
            project_dir=project_dir,
            project_name=project_name
        )

        self._tmp_dir = None

        self.db_installer = DatabaseInstaller(
            project_dir=project_dir, project_name=project_name,
            sudo=db_sudo, sudo_user=db_sudo_user
        )
        self.django_installer = DjangoInstaller(
            project_dir=project_dir, project_name=project_name
        )

    @property
    def requirements_file(self):
        return Path(
            self.install_path, 'requirements', 'base.txt'
        ).absolute()

    def create_tmp_dir(self):
        # TODO:
        # Account for existing project paths, here it should ask to remove
        # or abort.
        self._tmp_dir = Path(self.install_path, 'tmp')
        self._tmp_dir.mkdir()
        self._tmp_dir.chdir()

    def delete_tmp_dir(self):
        self.project_dir.chdir()
        self._tmp_dir.rmtree()
        self._tmp_dir = None

    def get_git_repo(self):
        self.create_tmp_dir()
        logger.info('Cloning repository ...')
        git.Git().clone(self.git_repo)

        #get last
        directory = self.git_repo.split('/')[-1:][0]
        #remove .git
        directory = directory.split('.')[0]
        self._tmp_dir = Path(self._tmp_dir, directory)
        logger.info('..done')


    def install_skeletton(self):
        logger.info('Installing %s' % self.flavor)
        move_orig = Path(self._tmp_dir, self.flavor)

        #move all items in the directory into the install_path
        for item in move_orig.listdir():
            item.move(self.install_path)
        self.delete_tmp_dir()
        logger.info('...done')

    def install_virtualenv(self):
        """
        Calls a script that creates the virtual environment and installs
        its dependencies, currently only sports python2.7 support.
        """
        exec_path = Path(Path(__file__).parent, 'bash', 'installer.sh')

        command = '%s %s %s %s' % (exec_path,
                                   self.install_path,
                                   self.project_name,
                                   self.requirements_file)

        logger.info('Installing virtualenv... (calling %s)' % command)
        run_command(command)

    def install_requirements(self):
        if not self.is_envwrapper:
            self.install_virtualenv()
        else:
            # we can assume that we are in the virtualenv now, and mkproject
            # was called
            command = 'pip install -r %s' % self.requirements_file
            run_command(command)

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
            target.write_file(content, 'w+')
            source.remove()

    def run_prepare_configuration(self):
        self.get_git_repo()
        self.install_skeletton()
        self.install_requirements()
        logger.info('Now installing Database ...')
        self.db_installer()
        logger.info('Now installing django...')
        self.django_installer()

    def run(self):
        self.run_prepare_configuration()
        self.run_create_configuration()
        self.run_post_create_configuration()

    def run_post_create_configuration(self):
        """
        run the the post_run_command_stack of all children.
        """

        for item in self.db_installer.post_run_command_stack:
            # should be a callable or None
            if item: item()

        for item in self.django_installer.post_run_command_stack:
            # should be a callable or None
            if item: item()

        self.move_to_venv(which_one='postactivate')
        self.move_to_venv(which_one='postdeactivate')

# run as a command line programm
# TODO: make it run as a command line program.
#if __name__ == '__main__':
#    if len(sys.argv) < 3:
#        logging.error('Insufficiant parameters')

#TODO:
# create security net for all the exceptions that could be raised ;-)