# exit when any command fails
set -e

# get path to demo directory
if [ "$SHELL" = "zsh" ]; then
   TEST_DIR="$( cd "$(dirname ${(%):-%N})" ; pwd -P )"
else
   TEST_DIR="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )";
fi

# set directories
APPS_DIR=${TEST_DIR}/..
API_DIR=${APPS_DIR}/api
CLI_DIR=${APPS_DIR}/cli

echo "API directory set to: $API_DIR"
echo "CLI directory set to: $CLI_DIR"
echo "APPS directory set to: $APPS_DIR"

# get shared isabl branch in case this test depends on a cross-repo change
ISABL_CLI_BRANCH=${ISABL_CLI_BRANCH:-${TRAVIS_PULL_REQUEST_BRANCH:-${TRAVIS_BRANCH:-master}}}
ISABL_API_BRANCH=${ISABL_API_BRANCH:-${TRAVIS_PULL_REQUEST_BRANCH:-${TRAVIS_BRANCH:-master}}}
echo "ISABL_CLI_BRANCH set to $ISABL_CLI_BRANCH"
echo "ISABL_API_BRANCH set to $ISABL_API_BRANCH"

# install isabl cli
[ ! -d $CLI_DIR ] && git clone git@github.com:isabl-io/cli.git $CLI_DIR
cd $CLI_DIR && (git checkout $ISABL_CLI_BRANCH || true) && pip install -r requirements.txt

# install current apps
cd $APPS_DIR && pip install -r requirements.txt

# clone api from github
[ ! -d $API_DIR ] && git clone git@github.com:isabl-io/api.git $API_DIR

# build container}
cd $API_DIR && (git checkout $ISABL_API_BRANCH || true) && docker-compose build && docker-compose up -d

# test current project
cd $APPS_DIR && py.test -vv --cov=mycli --cov-report=term-missing tests/ --commit
pylint mycli --rcfile=$APPS_DIR/.pylintrc
pydocstyle mycli --config=$APPS_DIR/.pydocstylerc
