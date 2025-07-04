.PHONY: install install-dev format lint type-check test clean help build build-clean install-browsers build-macos build-windows build-linux clean-build distribute

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  format       - Format code with Black and isort"
	@echo "  lint         - Run flake8 and pylint"
	@echo "  type-check   - Run mypy type checking"
	@echo "  test         - Run tests with pytest"
	@echo "  check        - Run format, lint, and type-check"
	@echo "  clean        - Remove Python cache files"
	@echo "  build        - Build application for current platform"
	@echo "  build-clean  - Clean build (removes previous build files)"
	@echo "  build-macos  - Build for macOS (manual)"
	@echo "  build-windows - Build for Windows (manual)"
	@echo "  build-linux  - Build for Linux (manual)"
	@echo "  install-browsers - Install Playwright browsers"
	@echo "  clean-build  - Remove build directories"
	@echo "  distribute   - Create distribution package with instructions"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Formatting
format:
	black .
	isort .

format-check:
	black --check .
	isort --check-only .

# Linting
lint:
	flake8 .
	pylint visa_autofill.py

# Type checking
type-check:
	mypy visa_autofill.py

# Testing
test:
	pytest

test-cov:
	pytest --cov=visa_autofill --cov-report=html

# Combined checks
check: format-check lint type-check

# Building
install-browsers:
	python3 -m playwright install chromium

build:
	python3 build_app.py

build-clean:
	rm -rf build dist
	python3 build_app.py

# Platform-specific builds (manual)
build-macos:
	pyinstaller visa_gui.spec --clean

build-windows:
	pyinstaller visa_gui_windows.spec --clean

build-linux:
	pyinstaller visa_gui_linux.spec --clean

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage

clean-build:
	rm -rf build dist

# Distribution
distribute:
	python3 create_distribution.py 