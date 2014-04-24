__author__ = 'Felix'
import string

from .installer import Installer
from .utils import generate_unique_id, run_command, logger


class DatabaseInstaller(Installer):
    #postgres implementation
    sql = ["\"CREATE USER %(db_user)s WITH PASSWORD '%(db_pw)s';\"",
           "\"CREATE DATABASE %(db_name)s with OWNER=%(db_user)s;\""
    ]

    sudo = False
    sudo_user = 'postgres'

    postactivate = '''
        # Database settings
        export DB_ENGINE='django.db.backends.postgresql_psycopg2'
        export DB_NAME='%(db_name)s'
        export DB_PW='%(db_pw)s'
        export DB_USER='%(db_user)s'
        export DB_HOST='localhost'
        export DB_PORT=''
    '''

    postdeactivate = '''
        #unset database
        unset DB_ENGINE
        unset DB_NAME
        unset DB_PW
        unset DB_USER
        unset DB_HOST
        unset DB_PORT
    '''
    def __init__(self, project_dir, project_name, sudo=False,
                 sudo_user=None, *args, **kwargs):
        if sudo:
            self.sudo = sudo

        if sudo_user:
            self.sudo_user = sudo_user

        super(DatabaseInstaller, self).__init__(
            project_dir=project_dir, project_name=project_name, *args, **kwargs
        )

        self.var_dict = dict(
            db_user=self.db_user, db_pw=self.db_pw, db_name=self.db_name
        )

    def _generate_db_pw(self):
        return u'%s' % generate_unique_id(length=20)

    def _generate_db_user(self):
        return u'%s_%s' % (self.project_name, generate_unique_id(
            length=10, chars=string.ascii_lowercase)
        )

    def _generate_db_name(self):
        return u'%s_%s_%s' % (
            self.project_name,
            generate_unique_id(length=3, chars=string.ascii_lowercase),
            generate_unique_id(
                length=3, chars=string.digits + string.ascii_lowercase)
        )

    @property
    def db_pw(self):
        """
        returns a db_pw that is generated once and then cached.
        """
        if not getattr(self, '_db_pw_cache', False):
            self._db_pw_cache = self._generate_db_pw()
        return self._db_pw_cache

    @property
    def db_user(self):
        """
        returns a db_user that is generated once and then cached.
        """
        if not getattr(self, '_db_user_cache', False):
            self._db_user_cache = self._generate_db_user()
        return self._db_user_cache

    @property
    def db_name(self):
        """
        returns a db_name that is generated once and then cached.
        """
        if not getattr(self, '_db_name_cache', False):
            self._db_name_cache = self._generate_db_name()
        return self._db_name_cache

    def create_sql(self):
        logger.info('creating sql with variables...')
        self.sql = [sql % self.var_dict for sql in self.sql]

    def run_prepare_configuration(self):
        self.create_sql()

        logger.info('Running SQL...')

        command_prefix = 'sudo su %s -c ' % self.sudo_user if self.sudo else ''

        for sql in self.sql:
            command = '%s psql -d postgres -c %s' % (command_prefix, sql)
            logger.info('running %s ' % command)
            run_command(command)

