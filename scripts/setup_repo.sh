#! /bin/bash

if test gecho &> /dev/null; then
	ECHO_CMD="gecho"
else
	ECHO_CMD="echo"
fi

if [ ! -d ".git" ]; then
	${ECHO_CMD} "ERROR: Only run from the repo root to set the pyenv for the repo directory."
	exit 1
fi

####
# Python env
#
# https://github.com/pyenv/pyenv
####

${ECHO_CMD} -n "Checking pyenv ......................... "
if ! type pyenv &> /dev/null; then
	${ECHO_CMD} -e -n "\33[2K\rInstalling pyenv ....................... "
	curl https://pyenv.run | bash
fi
${ECHO_CMD} "$(pyenv --version)"

${ECHO_CMD} -n "Checking python ........................ "
if [[ "3.12" = *"$(pyenv versions)"* ]]; then
	${ECHO_CMD} -e -n "\33[2K\rInstalling python ....................... "
	pyenv install 3.12
fi
pyenv local 3.12
${ECHO_CMD} $(python --version) "(pyenv: $(pyenv local))"


####
# Nox - test automation
#
# https://github.com/cjolowicz/nox
# https://nox.thea.codes/en/stable/
# https://github.com/cjolowicz/nox-poetry
####

${ECHO_CMD} -n "Checking nox ........................... "
if ! type nox &> /dev/null ; then
	${ECHO_CMD} -e -n "\33[2K\rInstalling nox ......................... "
	result=$(pipx install nox 2>&1)
	if [[ "$?" != "0" ]]; then
		${ECHO_CMD} "FAILED"
	    ${ECHO_CMD} "    pipx > $result"
	    exit 2
	fi
fi
${ECHO_CMD} -n $(nox --version | head -n 1)

${ECHO_CMD} -n "Checking nox-poetry .................... "
result=$(pipx inject nox nox-poetry 2>&1)
if [[ "$?" == "0" ]]; then
	${ECHO_CMD} "INSTALLED"
else
	${ECHO_CMD} "FAILED"
    ${ECHO_CMD} "    pipx > $result"
    exit 2
fi

####
# venv - isolate python dependencies
#
# Directly use venv instead of Poetry's virtual environment to integrate with IDEs.
# https://docs.python.org/3/library/venv.html
####
${ECHO_CMD} -n "Checking .venv/ ........................ "
if [[ ! -d ".venv/" ]]; then
	${ECHO_CMD} -e -n "\33[2K\rCreating .venv/ ........................ "
	result=$(python -m venv .venv 2&>1)
	if [[ "$?" == "0" ]]; then
		${ECHO_CMD} "CREATED"
	else
		${ECHO_CMD} "FAILED"
		${ECHO_CMD} "    venv > $result"
		exit 3
	fi
fi
${ECHO_CMD} "EXISTS"

####
# pre-commit - git hooks
#
# https://pre-commit.com/
####

${ECHO_CMD} -n "Checking pre-commit .................... "
if ! type pre-commit &> /dev/null; then
	${ECHO_CMD} -e -n "\33[2K\rInstalling pre-commit .................. "
	result=$(pipx install pre-commit)
	if [[ "$?" != "0" ]]; then
		${ECHO_CMD} "FAILED"
	    ${ECHO_CMD} "    pipx > $result"
	    exit 2
	fi
fi
${ECHO_CMD} $(pre-commit --version)

${ECHO_CMD} -n "Installing pre-commit in local repo .... "
result=$(pre-commit install --install-hooks)
if [[ "$?" != "0" ]]; then
	${ECHO_CMD} "FAILED"
	${ECHO_CMD} "    pre-commit > $result"
	exit 4
else
	${ECHO_CMD} "INSTALLED"
fi


####
# Poetry - dependency management and packaging
#
# https://python-poetry.org/docs/basic-usage/
####
${ECHO_CMD} -n "Checking poetry ........................ "
result=$(pipx install poetry 2>&1)
if [[ "$?" == "0" ]]; then
	${ECHO_CMD} $(poetry --version)
else
	${ECHO_CMD} "FAILED"
    ${ECHO_CMD} "    pipx > $result"
    exit 2
fi

${ECHO_CMD} "Installing dependencies in .venv/ ...... "
poetry install --with dev


####
# END
####
${ECHO_CMD} "This repository is ready for development."
