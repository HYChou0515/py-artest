all: build

test:
	pytest

build: style test
	poetry build

publish: build
	POETRY_PYPI_TOKEN_PYPI="${POETRY_PYPI_TOKEN_PYPI}" poetry publish -r test-pypi

style:
	isort .
	find . -name "*.py" | xargs autoflake --remove-all-unused-imports --remove-unused-variables --in-place
	black .

clean:
	rm -rf dist
	rm -rf .pytest_cache
