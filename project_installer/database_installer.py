__author__ = 'Felix'
import logging

from .installer import Installer
from .utils import generate_unique_id, run_command

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class DatabaseInstaller(Installer):
    #postgres implementation
    sql = ["\"CREATE USER '%(db_user)s' WITH PASSWORD '%(db_pw)s';\"",
           "\"CREATE DATABASE %(db_name)s with OWNER=%(db_user)s;\""
    ]

    sudo = False
    sudo_user = 'postgres'

    postactivate = "# Database settings \n" \
                   "export DB_ENGINE='django.db.backends.postgresql_psycopg2'\n" \
                   "export DB_NAME='%(db_name)s' \n" \
                   "export DB_PW='%(db_pw)s' \n" \
                   "export DB_USER='%(db_user)s' \n" \
                   "export DB_HOST='localhost' \n" \
                   "export DB_PORT='' \n"

    postdeactivate = "#unset database \n" \
                     "unset DB_ENGINE \n" \
                     "unset DB_NAME \n " \
                     "unset DB_PW \n" \
                     "unset DB_USER \n" \
                     "unset DB_HOST \n" \
                     "unset DB_PORT \n"

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
        return u'%s_%s' % (self.project_name, generate_unique_id(length=10))

    def _generate_db_name(self):
        return u'%s_%s_%s' % (
            self.project_name,
            generate_unique_id(length=3),
            generate_unique_id(length=3)
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
        logging.info('creating sql with variables...')
        self.sql = [sql % self.var_dict for sql in self.sql]

    def run_commands(self):
        self.create_sql()

        logging.info('Running SQL...')

        command_prefix = 'sudo su %s -c ' % self.sudo_user if self.sudo else ''

        for sql in self.sql:
            command = '%s psql -d postgres -c %s' % (command_prefix, sql)
            logging.info('running %s ' % command)
            run_command(command)

