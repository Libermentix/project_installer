==================
 project_installer
==================
project_installer is a project skeletton installer for python. This is a fork and
based on `virtualenvwrapper.django`_.

It can be used in two ways:

- a readymade installer that can be customized and implemented in a standalone-python script, 
  which will install a virtualenvironment, a database and a django-installation, plus accordingrequirements 
  set in the skeletton's requirements.

- a plugin template plugin for `virtualenvwrapper`_ to create new projects, which can be used with mkproject. 
  This will install the same except the virtualenvironmentsince it has been setup by the virtualenvwrapper already.

Currently the git repository points to `Virtualenv Skeletton Directory`_, this can
be adjusted when using the first approach


Installation
============

::

  $ pip install git+https://github.com/Libermentix/venv_project.git@master


Usage
=====

Custom Installscript
--------------------
1) Create a python script, make sure the package is in your PYTHONPATH

::

      #!/usr/bin/env python

      from project_installer import ProjectInstaller

      installer = ProjectInstaller(
                        path=<PATH_TO_PROJECT_DIR>, project_name='<PROJECT_NAME>'
      )
      installer()



2) You can adjust the following variables:

   - flavor = 'django_custom' #current default, needs to be a subdirectory git repo
   - git_repo = 'https://github.com/Libermentix/venv_skeletton_directory.git'
   - postactivate='<ENVIRONMENT VARIABLES TO BE SET> \n'
   - postdeactivate='<ENVIRONMENT VARIABLES TO BE DELETED> \n'
   - settings_module='settings.base' #relevant for django installations
   - is_production=True or False #relevant for django installations
   - settings_module = 'settings.base' #relevant for django installations
   - is_production = False #relevant for django installations
   - domain_prefix = 'www' #relevant for django installations
   - media_prefix = 'upload.cdn.' #relevant for django installations
   - static_prefix = 'static.cdn.' #relevant for django installations
   - domain = '.com' #relevant for django installations


Virtualenvwrapper integration
-----------------------------
::

  $ mkproject -t custom_project my_project_site


Extension and Modification
--------------------------
This project setup is based on a custom class based Installer system.
It can thus be easily extended.


Todos:
======
1) extend tests 
2) extend documentation


Forked from `virtualenvwrapper.django`_  to allow for a more flexible project setup.  


.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
.. _virtualenvwrapper.django: https://bitbucket.org/dhellmann/virtualenvwrapper.django
.. _Virtualenv Skeletton Directory: https://github.com/Libermentix/venv_skeletton_directory

