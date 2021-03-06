__author__ = 'Felix'
from unipath import Path
import git

from .installer import Installer
from .database_installer import DatabaseInstaller
from .django_installer import DjangoInstaller
from .utils import logger, add_trailing_slash



class ProjectInstaller(Installer):

    flavor = 'django_custom'
    git_repo = 'https://github.com/Libermentix/project_skeletton_directory.git'

    def __init__(self, project_dir, project_name,
                 db_sudo=False, db_sudo_user=None, *args, **kwargs):

        super(ProjectInstaller, self).__init__(
            project_dir, project_name, *args, **kwargs
        )

        self.var_dict = dict(
            project_dir=add_trailing_slash(project_dir),
            project_name=add_trailing_slash(project_name)
        )

        self._tmp_dir = None

        if self.install_path.exists():
            self.install_path.rmtree()

        self.db_installer = DatabaseInstaller(
            project_dir=project_dir, project_name=project_name,
            sudo=db_sudo, sudo_user=db_sudo_user
        )
        self.django_installer = DjangoInstaller(
            project_dir=project_dir, project_name=project_name
        )

    def run(self):
        self.run_prepare_configuration()
        self.run_create_configuration()
        self.run_post_create_configuration()

    def run_prepare_configuration(self):
        self.get_git_repo()
        self.install_skeletton()
        self.install_requirements()


    def run_post_create_configuration(self):
        """
        run the the post_run_command_stack
        """
        self.db_installer()
        self.django_installer()

        self.move_to_venv(which_one='postactivate')
        self.move_to_venv(which_one='activate')

        self.finish_queued_commands()

        #run the post create configuration command for the children
        for item in self.db_installer.post_run_command_stack:
            # should be a callable or None
            if item: item()

        for item in self.django_installer.post_run_command_stack:
            # should be a callable or None
            if item:
                logger.info('%s: Executing a django_installer_script ...' % item)
                item()


    @property
    def requirements_file(self):
        return Path(
            self.install_path, 'requirements', 'base.txt'
        ).absolute()

    @property
    def repo_dir(self):
        #get last
        directory = self.git_repo.split('/')[-1:][0]
        #remove .git
        directory = directory.split('.')[0]
        return Path(self._tmp_dir, directory)

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

    def get_git_repo(self):
        self.create_tmp_dir()
        logger.info('Cloning repository ...')

        if self.repo_dir.exists():
            logger.info('Repo dir exists removing it...')
            self.repo_dir.rmtree()

        git.Git().clone(self.git_repo)
        logger.info('..done')

    def install_skeletton(self):
        logger.info('Installing %s' % self.flavor)

        source = Path(self.repo_dir, self.flavor)

        #move all items in the directory into the install_path
        for item in source.listdir():
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
        self.run_command(command)

    def install_requirements(self):
        if not self.is_envwrapper:
            self.install_virtualenv()
        else:
            # we can assume that we are in the virtualenv now, and mkproject
            # was called
            command = 'pip install -r %s' % self.requirements_file
            self.run_command(command)




