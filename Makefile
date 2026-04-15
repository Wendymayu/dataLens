.PHONY: help install install-dev run test clean lint format

help:
	@echo "NL2SQL Agent - Available Commands"
	@echo "===================================="
	@echo "make install       - Install dependencies"
	@echo "make install-dev   - Install dev dependencies"
	@echo "make run           - Run the application"
	@echo "make test          - Run tests"
	@echo "make lint          - Run code linting"
	@echo "make format        - Format code"
	@echo "make clean         - Clean up temporary files"
	@echo "make requirements  - Generate requirements.txt"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python main.py

test:
	pytest test_example.py -v

lint:
	flake8 *.py --max-line-length=100
	mypy *.py --ignore-missing-imports

format:
	black *.py
	isort *.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info

requirements:
	pip freeze > requirements.txt

.DEFAULT_GOAL := help
