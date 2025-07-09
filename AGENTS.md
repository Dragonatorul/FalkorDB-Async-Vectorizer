# AGENTS.md

## Build/Lint/Test Commands
- **Install dependencies:** `pip install -r requirements.txt`
- **Lint (recommended):** `python -m flake8 vector_backfill_job.py` (install flake8 if needed)
- **Format:** `python -m black vector_backfill_job.py` (install black if needed)
- **Test:** No test files found; add tests using `pytest` for future testing.

## Code Style Guidelines
- **Imports:** Standard library first, then third-party, then local; one per line.
- **Formatting:** Use [black](https://black.readthedocs.io/) for auto-formatting.
- **Types:** Use type hints for all function signatures and variables.
- **Naming:** Use snake_case for variables/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants.
- **Error Handling:** Use try/except, log errors with `logger.error`, and re-raise if needed.
- **Logging:** Use the `logging` module, not print.
- **Configuration:** Use environment variables with defaults.
- **Dependencies:** All in `requirements.txt`.
- **No test framework or test files present; add tests in future PRs.**
- **No Cursor or Copilot rules found.**
