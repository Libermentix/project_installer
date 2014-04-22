#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Felix Plitzko.  All rights reserved.
#
"""
Create a project using a custom git-repository skeletton.

"""

import logging
import os
import subprocess

log = logging.getLogger('virtualenvwrapper.custom_project')
from project_installer.project_installer import ProjectInstaller

def template(args):
    """
    Runs a Django and runs django-admin to create a new project.
    """

    project, project_dir = args
    log.info('Installing %s in %s' % (project, project_dir))

    installer = ProjectInstaller(project_dir=project_dir,
                                 project_name=project,
                                 envwrapper=True)

    installer()


    return
