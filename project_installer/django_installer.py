__author__ = 'Felix'
import string

from unipath import Path

from .installer import Installer
from .utils import generate_unique_id, add_trailing_slash, logger



class DjangoInstaller(Installer):

    settings_module = 'settings.base'
    is_production = False
    domain_prefix = 'www.'
    media_prefix = 'upload.cdn.'
    static_prefix = 'static.cdn.'
    tld = '.com'

    def __init__(self, project_dir, project_name, *args, **kwargs):
        super(DjangoInstaller, self).__init__(
            project_dir=project_dir, project_name=project_name, *args, **kwargs
        )

        self._django_secret_key_cache = False

        self.var_dict = dict(
            settings_module=self.settings_module,
            django_debug=self.django_debug,
            django_secret_key=self.django_secret_key,
            django_media_url=self.django_media_url,
            django_static_url=self.django_static_url,
            django_website_url=self.django_website_url
        )

    def django_get_secret_key(self):
        if not getattr(self, '_django_secret_key_cache', False):
            string_choices = string.ascii_lowercase + \
                             string.ascii_uppercase \
                             + string.digits + \
                             '!@#%^&*_-+=:;/?.>,<~'

            self._django_secret_key_cache = \
                generate_unique_id(length=50, chars=string_choices)

        return self._django_secret_key_cache

    def get_django_url(self, which_one):
        prefix = getattr(self, '%s_prefix' % which_one)
        url = '%s%s%s' % (prefix, self.project_name, self.tld)

        return add_trailing_slash(url)

    def get_django_debug(self):
        return not self.is_production

    def get_website_url(self):
        return_string = ''

        if not self.is_production:
            return_string += 'test.'
        return_string += '%s%s%s' % (self.domain_prefix,
                                     self.project_name, self.tld)

        return return_string

    @property
    def django_secret_key(self):
        return self.django_get_secret_key()

    @property
    def django_debug(self):
        return self.get_django_debug()

    @property
    def django_media_url(self):
        return self.get_django_url('media')

    @property
    def django_static_url(self):
        return self.get_django_url('static')

    @property
    def django_website_url(self):
        return self.get_website_url()

    def install_django_database_schema(self):
        exec_path = Path(Path(__file__).parent, 'bash', 'django_installer.sh')
        logger.info('Installing database schema ...')
        command = '%s %s' % (exec_path, self.project_name)

        self.run_command(command)

        logger.info('...done')

    def run_prepare_configuration(self):
        self.post_run_command_stack.append(
            self.install_django_database_schema
        )



