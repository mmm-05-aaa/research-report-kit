# Research Report Kit

A standalone, local-first CSV quality inspector for people who need to understand a table before cleaning, reporting, or analysing it.

It is part of a local productivity-tool portfolio, but it remains independent from the Desktop File Organizer: separate repository, runtime, tests, output and release lifecycle.

## What it checks

- encoding and delimiter
- row and column counts
- missing values by column
- duplicate rows
- irregular row widths
- duplicate or empty header labels
- numeric versus text columns
- numeric minimum, maximum, mean and median
- non-finite values such as `NaN` and `Inf`

Every run records the source file's SHA-256 and writes three local reports:

```text
summary.json   machine-readable results
report.md      portable review document
report.html    visual report for browsers and screenshots
```

The source CSV is read-only and is never uploaded or changed.

## Native interface

On Windows, double-click:

```text
run_gui.bat
```

The interface lets you select a CSV, choose a report folder, generate the report bundle and open the HTML report. The included synthetic demo is preselected on first launch.

You can also run the installed command:

```bash
reportkit-gui
```

## Command line

No third-party runtime dependency is required.

```bash
python -m reportkit inspect examples/demo.csv --out demo-report
```

To print the JSON result as well:

```bash
python -m reportkit inspect examples/demo.csv --out demo-report --json
```

Open `demo-report/report.html` in a browser after the command completes.

## Install for development

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m unittest discover -s tests -v
```

Supported Python versions: 3.10, 3.11 and 3.12.

## Safety and privacy

- local processing only
- no network calls
- no source-file writes
- no silent row deletion or missing-value imputation
- no business or scientific conclusions
- HTML content is escaped before rendering
- synthetic example data only in the repository

The report identifies structural signals; a domain owner must decide what they mean and whether any correction is appropriate.

## Current scope

Version `0.2.0` supports CSV inspection and report generation. It does not yet support Excel workbooks, automated cleaning, database connections or large-file streaming. These are intentional product boundaries, not implied features.

## Tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the suite on Windows with Python 3.10, 3.11 and 3.12.

## Project structure

```text
reportkit/core.py       CSV parsing and quality summary
reportkit/reporting.py  JSON, Markdown and safe HTML reports
reportkit/cli.py        command-line interface
reportkit/gui.py        standalone native interface
tests/                  behavior and regression tests
examples/               synthetic demonstration data
```

## Screenshots

Screenshots will be added after the native interface and generated HTML report are reviewed on Windows. No private or customer data should appear in repository images.

## License

MIT © 2026 mmm-05-aaa
