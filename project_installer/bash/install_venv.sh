#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh

#set cflags OSX:
# credits to http://satishgandham.com/2014/04/error-command-cc-failed-with-
# exit-status-1-cant-install-pil-pillow-mysql-and-other-packages-in-mavericks/
export CFLAGS=-Qunused-arguments
export CPPFLAGS=-Qunused-arguments

PROJECTPATH=$1
VENVNAME=$2
REQUIREMENTS=$3

PYTHON_EXEC=$(which python2.7)

#test whether we pass requirements.
if [ -n REQUIREMENTS ]
then
    mkvirtualenv -a ${PROJECTPATH} -r ${REQUIREMENTS} -p ${PYTHON_EXEC} ${VENVNAME}
else
    mkvirtualenv -a ${PROJECTPATH} ${VENVNAME}
fi
