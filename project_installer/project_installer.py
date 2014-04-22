__author__ = 'Felix'
import logging

from subprocess import Popen, PIPE
from threading import Thread

from unipath import Path
import git

from .installer import Installer
from .database_installer import DatabaseInstaller
from .django_installer import DjangoInstaller
from .utils import printer, stream_watcher


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class ProjectInstaller(Installer):
    postactivate = '#!/bin/bash' \
                   '#setting project related variables' \
                   'export PROJECT_NAME="%(project_name)s"\n' \
                   'export PROJECT_PATH="$%(project_dir) \n" ' \
                   'echo "virtual environment for application in project path: $PROJECT_PATH" \n' \
                   '#extend python path \n' \
                   ' EXTENSION="" \n ' \
                   ' if [ -n "$PYTHONPATH" ] ; then \n' \
                   '     OLD_PYTHON_PATH="$PYTHONPATH" \n ' \
                   '     export OLD_PYTHON_PATH \n' \
                   '     EXTENSION=":${OLD_PYTHON_PATH}" \n' \
                   ' fi \n' \
                   ' export PYTHONPATH=${PROJECT_PATH}${EXTENSION} \n'

    postdeactivate = '#unsetting project related variables' \
                     'unset PROJECT_BASE_PATH \n ' \
                     'unset PROJECT_NAME \n' \
                     'unset PROJECT_PATH \n' \
                     'export PYTHONPATH=${OLD_PYTHON_PATH} \n'

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
        logging.info('Cloning repository ...')
        git.Git().clone(self.git_repo)

        #get last
        directory = self.git_repo.split('/')[-1:][0]
        #remove .git
        directory = directory.split('.')[0]
        self._tmp_dir = Path(self._tmp_dir, directory)
        logging.info('..done')


    def install_skeletton(self):
        logging.info('Installing %s' % self.flavor)
        move_orig = Path(self._tmp_dir, self.flavor)

        #move all items in the directory into the install_path
        for item in move_orig.listdir():
            item.move(self.install_path)
        self.delete_tmp_dir()
        logging.info('...done')

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

        logging.info('Installing virtualenv... (calling %s)' % command)
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

        Thread(target=stream_watcher, name='stdout-watcher',
                args=('STDOUT', proc.stdout)).start()
        Thread(target=stream_watcher, name='stderr-watcher',
                args=('STDERR', proc.stderr)).start()
        Thread(target=printer, name='printer').start()


    def install_requirements(self):
        if not self.is_envwrapper:
            self.install_virtualenv()
        else:
            # we can assume that we are in the virtualenv now, and mkproject
            # was called
            command = 'pip install -r %s' % self.requirements_file

            proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

            Thread(target=stream_watcher, name='stdout-watcher',
                    args=('STDOUT', proc.stdout)).start()
            Thread(target=stream_watcher, name='stderr-watcher',
                    args=('STDERR', proc.stderr)).start()
            Thread(target=printer, name='printer').start()

            #process = subprocess.Popen(
            #    command, shell=True,
            #    stdout=subprocess.PIPE,
            #    stderr=subprocess.STDOUT
            #)
            #process.communicate()
            #for line in process.stdout:
            #    logging.info(line)

    def move_to_venv(self, which_one):
        """
        Moves the created config_files into the bin folder to be executed.
        """
        target = Path(self.venv_folder, 'bin')
        move_orig = Path(self.install_path, which_one)

        if move_orig.exists():
            logging.info('Moving %s into place ...' % which_one)
            move_orig.move(target)

    def run_commands(self):
        self.get_git_repo()
        self.install_skeletton()
        self.install_requirements()
        self.db_installer()
        self.django_installer()
        self.move_to_venv(which_one='postactivate')
        self.move_to_venv(which_one='postdeactivate')


# run as a command line programm
# TODO: make it run as a command line program.
#if __name__ == '__main__':
#    if len(sys.argv) < 3:
#        logging.error('Insufficiant parameters')
