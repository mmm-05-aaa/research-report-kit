import csv
import hashlib
import io
import json
import math
import statistics
from pathlib import Path

from .reporting import write_report_bundle

MISSING_MARKERS = {"", "na", "n/a", "nan", "null", "none"}


def _missing(value: str) -> bool:
    return value.strip().lower() in MISSING_MARKERS


def _read_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the CSV as UTF-8 or GB18030")


def _dialect(text: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def _number(value: str) -> float | int | None:
    value = value.strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def summarize_csv(source: str | Path) -> dict:
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    text, encoding = _read_text(path)
    dialect = _dialect(text)
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), dialect, strict=True))
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from exc
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError("CSV is empty")

    header = rows[0]
    width = len(header)
    body = [row + [""] * (width - len(row)) for row in rows[1:]]
    irregular_rows = sum(1 for row in rows[1:] if len(row) != width)
    missing_by_column = [sum(_missing(row[index]) for row in body) for index in range(width)]
    duplicate_rows = len(body) - len({tuple(row) for row in body})

    columns = []
    for index, name in enumerate(header):
        values = [row[index] for row in body]
        non_empty = [value for value in values if not _missing(value)]
        numbers = [number for number in (_number(value) for value in non_empty) if number is not None]
        numeric = bool(non_empty) and len(numbers) == len(non_empty)
        column = {
            "name": name or f"column_{index + 1}",
            "missing": missing_by_column[index],
            "non_empty": len(values) - missing_by_column[index],
            "type": "numeric" if numeric else "text",
        }
        if numeric:
            column["statistics"] = {
                "min": min(numbers),
                "max": max(numbers),
                "mean": statistics.fmean(numbers),
                "median": statistics.median(numbers),
            }
        columns.append(column)

    issues = []
    if len(set(header)) != len(header):
        issues.append("duplicate_header_labels")
    if any(not name.strip() for name in header):
        issues.append("empty_header_labels")
    if irregular_rows:
        issues.append("irregular_row_widths")

    return {
        "source": path.name,
        "source_name": path.name,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "encoding": encoding,
        "delimiter": dialect.delimiter,
        "rows": len(body),
        "columns": width,
        "missing_values": sum(missing_by_column),
        "duplicate_rows": duplicate_rows,
        "irregular_rows": irregular_rows,
        "issues": issues,
        "column_summary": columns,
    }


def write_summary(summary: dict, output: str | Path) -> Path:
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    target = output_path / "summary.json"
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target

