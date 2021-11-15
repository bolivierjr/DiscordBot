test-all: test pre-commit

test:
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml run --rm bot-test pytest -vvvs

pre-commit:
	pre-commit run --all-files

isort:
	isort .

black:
	black --line-length=120 ./

lint:
	flake8 ./

all: isort black lint

.PHONY: all
