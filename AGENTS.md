# Instructions for contributors and agents

## Project overview

MPP Tools is a Python project that retrieves portfolio data from Mon Petit Placement and stores it locally in SQLite. It then generates reports from that local data.

- `src/extract_data/`: fetches and persists portfolio data.
- `src/shared/`: shared models, database access, and sampling helpers.
- `src/build_html_report/`: produces the interactive HTML report.
- `src/build_md_report/`: produces the Markdown report for analysis tools such as NotebookLM.

## Development guidelines

- Keep data processing local. Do not add calls that upload portfolio data to third parties.
- Treat `.env` files, account IDs, API credentials, SQLite databases, generated reports, and logs as private data. Never commit or expose their contents.
- Reuse the dataclasses in `src/shared/models.py` and data access functions in `src/shared/report.py`; avoid duplicating database queries in report builders.
- Keep the HTML and Markdown reports semantically aligned: summary, capital history, positions, and product history should describe the same data.
- The Markdown report must remain plain Markdown and self-contained: no HTML, JavaScript, external charts, or images required to understand the data.
- Replace chart information in Markdown with compact monthly tables. Use the latest valuation available in each month.

## Python conventions

- Target Python 3.10+ and use type annotations for new or changed public functions.
- Prefer small, pure rendering helpers in report builders.
- Sort data explicitly when chronological or amount ordering matters.
- Gracefully handle empty collections and missing optional product metadata.
- Write generated text as UTF-8.

## Verification

- At minimum, compile changed Python modules: `python -m py_compile <files>`.
- Run the affected report builder with a configured local `.env` and SQLite database when available.
- Confirm generated Markdown contains the expected headings and tables, and no `<html>` or `<script>` tags.
- Do not overwrite unrelated generated artifacts or user changes.

## Shell scripts

- `setup.sh` provisions Python virtual environments.
- `run.sh` is intended for scheduled Linux execution; keep its commands non-interactive and fail clearly when a required step fails.
