# Research Report Kit

Local-first CSV inspection for reproducible research and business data reports.

## First phase

The first phase reads a CSV without changing it and writes a stable `summary.json` containing:

- encoding and delimiter
- row and column counts
- missing values
- duplicate rows
- irregular row widths
- per-column type and numeric statistics

## Quick start

```bash
python -m reportkit inspect examples/demo.csv --out report --json
```

The command writes `report/summary.json`. It uses only the Python standard library.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Scope and safety

This project is intentionally read-only in phase one. It does not upload data, modify the source CSV, infer scientific conclusions, or silently remove observations. Use synthetic or public data in the repository.

## License

MIT
