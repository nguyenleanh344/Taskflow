install-dev:
	pip install -e ".[dev]"

test:
	pytest

format:
	ruff format .

format-check:
	ruff format --check .

check: format-check test