#!/bin/bash
PROJECTNAME=$1

workon ${PROJECTNAME}
django-admin.py syncdb
django-admin.py migrate