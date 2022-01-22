.DEFAULT_GOAL := test

.PHONY: install-reqs
install-reqs:
	pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: install-reqs-tests
install-reqs-tests: install-reqs
	pip install --upgrade -r requirements-tests.txt

.PHONY: brunette
brunette:
	brunette --check .

.PHONY: isort
isort:
	isort --check-only --diff .

.PHONY: flake8
flake8:
	flake8

.PHONY: mypy
mypy:
	mypy .

.PHONY: test
test: isort brunette flake8 mypy
