#!/bin/sh

#set -x

test_dir=$(dirname $0)

export WORKON_HOME="${TMPDIR:-/tmp}WORKON_HOME"
export PROJECT_HOME="${TMPDIR:-/tmp}PROJECT_HOME"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    rm -rf "$PROJECT_HOME"
    mkdir -p "$PROJECT_HOME"
    source "$test_dir/util.sh"
    load_virtualenvwrapper
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
    rm -rf "$PROJECT_HOME"
}

setUp () {
    echo
    rm -f "$TMPDIR/catch_output"
}

tearDown () {
    type deactivate >/dev/null 2>&1 && deactivate
}

test_create_project_files () {
    mkproject -t django myproject1
    for filename in myproject1 myproject1/__init__.py myproject1/urls.py
    do
        assertTrue "$filename not created" "[ -e $PROJECT_HOME/myproject1/myproject1/$filename ]"
    done
}

. "$test_dir/shunit2"
