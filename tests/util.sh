
load_virtualenvwrapper () {
    venvw=`which virtualenvwrapper.sh`
    echo "Test running in `pwd`"
    echo "Loading $venvw"
    source $venvw
}
