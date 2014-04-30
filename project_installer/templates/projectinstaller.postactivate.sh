#!/bin/bash
#setting project related variables
export PROJECT_NAME='{{ project_name }}'
export PROJECT_PATH='{{ project_dir }}{{ project_name }}'
echo "virtual environment for application in projectpath: ${PROJECT_PATH}"
#extend pythonpath
EXTENSION=""
if [ -n "$PYTHONPATH" ] ; then
    OLD_PYTHON_PATH="$PYTHONPATH"
    export OLD_PYTHON_PATH
    EXTENSION=":${OLD_PYTHON_PATH}"
fi
export PYTHONPATH=${PROJECT_PATH}${EXTENSION}
