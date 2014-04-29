__author__ = 'Felix'
import string

from unipath import Path

from .installer import Installer
from .utils import generate_unique_id, add_trailing_slash


class DjangoInstaller(Installer):

    settings_module = 'settings.base'
    is_production = False
    domain_prefix = 'www.'
    media_prefix = 'upload.cdn.'
    static_prefix = 'static.cdn.'
    domain = '.com'

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

    def get_django_media_url(self):
        media_url = '%s%s%s'
        return add_trailing_slash(media_url)

    def get_django_static_url(self):
       static_url = '%s%s%s'
       return add_trailing_slash(static_url)

    def get_django_debug(self):
        return not self.is_production

    def get_website_url(self):
        return_string = ''

        if not self.is_production:
            return_string += 'test.'
        return_string += '%s%s%s' % (self.domain_prefix,
                                     self.project_name, self.domain)

        return return_string

    @property
    def django_secret_key(self):
        return self.django_get_secret_key()

    @property
    def django_debug(self):
        return self.get_django_debug()

    @property
    def django_media_url(self):
        return self.get_django_media_url()

    @property
    def django_static_url(self):
        return self.get_django_static_url()

    @property
    def django_website_url(self):
        return self.get_website_url()

    def run_prepare_configuration(self):
        pass


