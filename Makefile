all: build

test:
	pytest --cov-report html --cov=artest tests/

build: style test
	poetry build

publish: build
	POETRY_PYPI_TOKEN_PYPI="${POETRY_PYPI_TOKEN_PYPI}" poetry publish -r test-pypi

style:
	pydocstyle artest --convention=google --ignore-decorator=override && \
	autoflake -r --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports --in-place artest tests && \
	isort artest tests && \
	black . && \
	ruff artest tests

clean:
	rm -rf dist
	rm -rf .pytest_cache
