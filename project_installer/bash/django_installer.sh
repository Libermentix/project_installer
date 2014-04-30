#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
VENVNAME=$1

workon $1
django-admin.py syncdb --noinput
django-admin.py migrate