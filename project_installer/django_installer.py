__author__ = 'Felix'
import string

from unipath import Path

from .installer import Installer
from .utils import generate_unique_id, run_command, logger


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

        self.var_dict = dict(
            settings_module=self.settings_module,
            django_debug=self.django_debug,
            django_secret_key=self.django_secret_key,
            django_media_url=self.django_media_url,
            django_static_url=self.django_static_url,
            django_website_url=self.django_website_url
        )

    @property
    def django_secret_key(self):
        string_choices = string.ascii_lowercase + string.ascii_uppercase \
                         + string.digits + '!@#%^&*()_-+=[]|:;/?.>,<`~'
        return generate_unique_id(length=50, chars=string_choices)

    @property
    def django_debug(self):
        if self.is_production:
            return False
        return True

    @property
    def django_media_url(self):
        return '%s%s%s' % (self.media_prefix, self.project_name, self.domain)

    @property
    def django_static_url(self):
        return '%s%s%s' % (self.static_prefix, self.project_name, self.domain)

    @property
    def django_website_url(self):
        return_string = ''
        if not self.is_production:
            return_string += 'test.'
        return_string += '%s%s%s' % (self.domain_prefix,
                                     self.project_name, self.domain)

        return return_string

    def run_prepare_configuration(self):
        # nothing to be run in django installer,
        # we just need to run the log files.
        logger.info('Doing nothing...')
