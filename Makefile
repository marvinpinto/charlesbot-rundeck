ENV=./env

all: help

help:
	@echo '-----------------------------------------'
	@echo ' Charlesbot Rundeck Plugin make targets'
	@echo '-----------------------------------------'
	@echo 'help: This help'
	@echo 'install: Install dev dependencies'
	@echo 'test: Run tests'
	@echo 'checkstyle: Run flake8'
	@echo 'run: Run CharlesBOT locally'

# Utility target for checking required parameters
guard-%:
	@if [ "$($*)" = '' ]; then \
     echo "Missing required $* variable."; \
     exit 1; \
   fi;

.PHONY: clean
clean:
	py3clean .
	rm -f .coverage
	find . -name "__pycache__" -exec /bin/rm -rf {} \;

.PHONY: clean-all
clean-all: clean
	rm -rf env
	rm -rf *.egg-info

env: clean
	test -d $(ENV) || pyvenv-3.4 $(ENV)

.PHONY: install
install: env
	$(ENV)/bin/pip install -r requirements-dev.txt
	$(ENV)/bin/pip install -e .

.PHONY: checkstyle
checkstyle: install
	$(ENV)/bin/flake8 --max-complexity 10 charlesbot_rundeck
	$(ENV)/bin/flake8 --max-complexity 10 tests

.PHONY: test
test: install
	$(ENV)/bin/nosetests \
		-v \
		--with-coverage \
		--cover-package=charlesbot_rundeck \
		tests

.PHONY: run
run:
	PYTHONWARNINGS=default PYTHONASYNCIODEBUG=1 $(ENV)/bin/charlesbot

# Helper make target to spin up a local (docker) rundeck server for you to test
# and iterate on
rundeck-server:
	docker run \
		-d \
		-v $(shell pwd)/bootstrap/framework.properties:/etc/rundeck/framework.properties \
		-v $(shell pwd)/bootstrap/tokens.properties:/etc/rundeck/tokens.properties \
		-v $(shell pwd)/bootstrap/apitoken.aclpolicy:/etc/rundeck/apitoken.aclpolicy \
		-p 4440:4440 \
		-e RUNDECK_PASSWORD=runduck \
		-e SERVER_URL=http://my.rundeck.test:4440 \
		-t jordan/rundeck:latest
	@echo "Be sure to have a '172.17.0.1 my.rundeck.test' entry in your /etc/hosts"

# Helper make target to bootstrap your local (docker) rundeck server with some
# boilerplate project + jobs, for you to get going!
rundeck-server-bootstrap:
	curl -X POST \
		-H "Content-Type: application/json" \
		-H "X-Rundeck-Auth-Token: baiY8aw4Ieng0aQuoo" \
		--data-binary "@bootstrap/test_project.json" \
		http://my.rundeck.test:4440/api/11/projects
	curl -X POST \
		-H "Content-Type: application/yaml" \
		-H "X-Rundeck-Auth-Token: baiY8aw4Ieng0aQuoo" \
		--data-binary "@bootstrap/test_job.yaml" \
		http://my.rundeck.test:4440/api/14/jobs/import?project=test-project

# e.g. PART=major make release
# e.g. PART=minor make release
# e.g. PART=patch make release
.PHONY: release
release: guard-PART
	$(ENV)/bin/bumpversion $(PART)
