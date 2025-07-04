# Visa Application Auto-Fill

This project provides a small Python script, `visa_autofill.py`, that reads applicant data from a CSV or Excel worksheet and automatically fills out an online visa-application form using [Playwright](https://playwright.dev/).

> **IMPORTANT**
> • You must update the field selectors inside `visa_autofill.py` (`FIELD_SELECTORS`, `SUBMIT_BUTTON_SELECTOR`, and `SUCCESS_SELECTOR`) so they match your actual visa-application website.
> • The script assumes you will log in to the site manually. Once logged in and on a blank "New Application" page, press **Enter** in the terminal and the automation will begin.

---

## Installation

```bash
# Clone or download this repo, then inside the project directory:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Playwright needs its browsers installed once per environment
python -m playwright install
```

---

## Development Setup

For development with linting and formatting:

```bash
# Install development dependencies
make install-dev

# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run all checks
make check

# Run tests
make test
```

### VS Code Setup

1. Install the Python extension
2. Install these extensions for better development experience:
   - Black Formatter
   - isort
   - Flake8
   - Pylint
   - MyPy Type Checker

The `.vscode/settings.json` file is configured to automatically format and lint your code on save.

---

## Preparing Your Data

1. Create a CSV or Excel file (e.g. `applicants.xlsx`).
2. Ensure the column headers match the keys defined in `FIELD_SELECTORS` inside the script. Example headers:

   | first_name | last_name | birth_date | passport_number |
   |------------|-----------|------------|-----------------|

---

## Running the Script

```bash
python visa_autofill.py applicants.xlsx --form-url "https://visa.gov/app/new" --output results.csv
```

Arguments:

* `data_file` (positional): Path to your CSV/Excel file.
* `--form-url` (required): URL of a **blank** application form. The script reloads this page for each applicant.
* `--output` (optional): Where to write a CSV summarising success/failure. Defaults to `submission_status.csv`.
* `--headless`: Run the browser without a visible window (only once everything works).

The script will:

1. Open the browser at `--form-url`.
2. Pause so you can log in and navigate to the blank form.
3. Iterate over each row, filling and submitting the form.
4. Write a CSV with a `status` (SUCCESS/FAILURE) and `error` column.

---

## Extending / Customising

* **Adding more fields** – Edit `FIELD_SELECTORS` so every data column is mapped to the correct CSS selector.
* **Different success criteria** – Change `SUCCESS_SELECTOR` to something unique on the "application submitted" confirmation page.
* **Additional logic** – If the site requires navigating through multiple steps, break `fill_form` into smaller functions and add the necessary Playwright commands.

---

## Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatter (like Prettier for Python)
- **isort**: Import sorting
- **Flake8**: Linting (like ESLint for Python)
- **Pylint**: Additional linting with more rules
- **MyPy**: Static type checking
- **Pytest**: Testing framework

### Available Commands

```bash
make help          # Show all available commands
make format        # Format code with Black and isort
make lint          # Run flake8 and pylint
make type-check    # Run mypy type checking
make check         # Run all checks (format, lint, type-check)
make test          # Run tests
make clean         # Clean up cache files
```

---

## Troubleshooting

### Browser Installation Issues

If you encounter browser installation errors like:
```
❌ Failed to launch browser: BrowserType.launch: Executable doesn't exist
```

**Quick Fixes:**
1. **Install Google Chrome** (easiest solution):
   - Visit https://www.google.com/chrome/
   - Download and install Google Chrome
   - Restart the application

2. **Run the fix script**:
   ```bash
   python3 fix_browser_install.py
   ```

3. **Test browser installation**:
   ```bash
   python3 test_browser_install.py
   ```

4. **Manual Playwright installation**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

**For detailed instructions, see [BROWSER_INSTALLATION.md](BROWSER_INSTALLATION.md)**

### Other Issues

1. **Timeout waiting for success confirmation** – Increase the timeout in `page.wait_for_selector`, or verify that `SUCCESS_SELECTOR` points to a real element.
2. **Wrong selectors** – Use your browser's dev tools (right-click ➜ Inspect) to find the precise `name`, `id`, or other attributes.
3. **Headless issues** – If it works with a visible browser but fails headlessly, add more `page.wait_for_*` calls or slow down operations with `page.wait_for_timeout()`.

---

## License

MIT 