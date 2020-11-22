SHELL = /bin/bash
VERSION = 0.7.33

# Make Python wheels
default: build

# Prepare VirtualEnv by installing project dependencies
venv/bin/activate: executor/requirements.txt
	test -d venv || python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r executor/requirements.txt
	touch venv/bin/activate

# Shortcut for preparation of VirtualEnv
venv: venv/bin/activate

check-venv:
ifndef VIRTUAL_ENV
	$(error Please create a VirtualEnv with 'make venv' and activate it)
endif

# Build the Python wheel install packages.
build: check-venv
	pushd executor; python ./setup.py bdist_wheel; popd

# Update version numbers, commit and tag 
bumpversion:
	bumpversion --verbose patch

# Clean temporary files
clean:
	rm -fr  executor/build
	rm -fr  executor/dist
	rm -fr  executor/*egg-info
	rm -f  ./.coverage
	find . -name "*.bak" -delete
	find . -name "__pycache__" -delete

# Clean cached Docker data and state
clean-docker:
	docker container prune
	docker volume prune
	docker system prune

