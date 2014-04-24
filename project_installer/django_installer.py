__author__ = 'Felix'
import string
import logging
from unipath import Path

from .installer import Installer
from .utils import generate_unique_id, run_command

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class DjangoInstaller(Installer):
    postactivate = '#django \n' \
                   'export DJANGO_SETTINGS_MODULE="%(settings_module)s"\n' \
                   'export DJANGO_SECRET_KEY="%(django_secret_key)s"\n' \
                   'export DJANGO_DEBUG="%(django_debug)s"\n' \
                   'export DJANGO_MEDIA_URL="http://%(django_media_url)s/"\n' \
                   'export DJANGO_STATIC_URL="http://%(django_static_url)s/"\n'\
                   'export DJANGO_WEBSITE_URL="http://%(django_website_url)s"\n'

    postdeactivate = '#django \n' \
                     'unset DJANGO_SETTINGS_MODULE \n' \
                     'unset DJANGO_SECRET_KEY \n' \
                     'unset DJANGO_DEBUG \n' \
                     'unset DJANGO_MEDIA_URL \n' \
                     'unset DJANGO_STATIC_URL \n' \
                     'unset DJANGO_WEBSITE_URL \n'

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
        logging.info('Doing nothing...')

    def run_post_create_configuration(self):
        self.post_run_command_stack.append(
            self._run_django_post_install_script()
        )

    def _run_django_post_install_script(self):
        exec_path = Path(Path(__file__).parent, 'bash', 'django_post_install.sh')
        command = '%s %s' % (exec_path, self.project_name)

        run_command(command)