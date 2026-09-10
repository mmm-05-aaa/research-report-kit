"""Human-readable report generation for Research Report Kit."""

from __future__ import annotations

import html
import json
from pathlib import Path


def _display(value: object) -> str:
    return html.escape(str(value), quote=True)


def _markdown(summary: dict) -> str:
    lines = [
        "# Data quality overview",
        "",
        f"- Source: `{summary['source']}`",
        f"- Rows: **{summary['rows']}**",
        f"- Columns: **{summary['columns']}**",
        f"- Missing values: **{summary['missing_values']}**",
        f"- Duplicate rows: **{summary['duplicate_rows']}**",
        f"- Irregular rows: **{summary['irregular_rows']}**",
        f"- Source SHA-256: `{summary['source_sha256']}`",
        "",
        "## Structural checks",
        "",
    ]
    lines += [f"- `{issue}`" for issue in summary["issues"]] or ["- No structural issues detected"]
    lines += [
        "",
        "## Column profile",
        "",
        "| Column | Type | Missing | Non-empty |",
        "|---|---|---:|---:|",
    ]
    for column in summary["column_summary"]:
        name = str(column["name"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {name} | {column['type']} | {column['missing']} | {column['non_empty']} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This report describes structural data-quality signals. It does not change the source file or infer business or scientific conclusions.",
    ]
    return "\n".join(lines) + "\n"


def _html(summary: dict) -> str:
    row_count = max(1, int(summary["rows"]))
    rows = []
    for column in summary["column_summary"]:
        missing = int(column["missing"])
        percent = min(100.0, missing / row_count * 100)
        rows.append(
            "<tr>"
            f"<td><strong>{_display(column['name'])}</strong></td>"
            f"<td><span class=\"pill\">{_display(column['type'])}</span></td>"
            f"<td>{missing}</td>"
            f"<td><div class=\"bar\"><span style=\"width:{percent:.1f}%\"></span></div>"
            f"<small>{percent:.1f}%</small></td>"
            "</tr>"
        )
    cards = [
        ("Rows", summary["rows"]),
        ("Columns", summary["columns"]),
        ("Missing", summary["missing_values"]),
        ("Duplicates", summary["duplicate_rows"]),
        ("Irregular rows", summary["irregular_rows"]),
    ]
    cards_html = "".join(
        f'<article class="card"><span>{_display(label)}</span><strong>{_display(value)}</strong></article>'
        for label, value in cards
    )
    issues_html = "".join(f"<li><code>{_display(issue)}</code></li>" for issue in summary["issues"])
    if not issues_html:
        issues_html = "<li>No structural issues detected</li>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data quality report · {_display(summary['source'])}</title>
<style>
:root{{--ink:#132238;--muted:#64748b;--line:#dbe4ee;--surface:#fff;--accent:#2563eb;--soft:#eff6ff;--warn:#d97706}}
*{{box-sizing:border-box}} body{{margin:0;background:#f4f7fb;color:var(--ink);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}}
main{{max-width:1080px;margin:40px auto;padding:0 24px}} header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:24px}}
h1{{font-size:32px;line-height:1.15;margin:6px 0}} .eyebrow{{color:var(--accent);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:12px}}
.source{{color:var(--muted);word-break:break-all}} .grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:22px 0}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 4px 16px #17355b0a}}
.card span{{display:block;color:var(--muted);font-size:13px}} .card strong{{display:block;font-size:26px;margin-top:5px}}
.panel{{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 6px 24px #17355b0b}} .issues{{margin-bottom:16px}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid var(--line);padding:13px 10px;text-align:left}} th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}}
.pill{{display:inline-block;background:var(--soft);color:var(--accent);border-radius:999px;padding:3px 9px;font-size:12px;font-weight:650}}
.bar{{display:inline-block;width:150px;height:8px;background:#e8eef5;border-radius:999px;overflow:hidden;margin-right:9px;vertical-align:middle}} .bar span{{display:block;height:100%;background:var(--accent)}}
.notice{{border-left:4px solid var(--accent);background:var(--soft);padding:14px 16px;margin-top:20px;border-radius:0 10px 10px 0}} small{{color:var(--muted)}}
@media(max-width:760px){{.grid{{grid-template-columns:repeat(2,1fr)}} header{{display:block}} .panel{{overflow-x:auto}}}}
</style>
</head>
<body><main>
<header><div><div class="eyebrow">Local · Read-only · Reproducible</div><h1>Data quality overview</h1><div class="source">{_display(summary.get('source_name', Path(str(summary['source'])).name))} · {_display(summary['encoding'])} · delimiter {_display(repr(summary['delimiter']))}</div></div></header>
<section class="grid">{cards_html}</section>
<section class="panel issues"><h2>Structural checks</h2><ul>{issues_html}</ul><small>Source SHA-256: {_display(summary['source_sha256'])}</small></section>
<section class="panel"><h2>Column profile</h2><table><thead><tr><th>Column</th><th>Detected type</th><th>Missing</th><th>Missing rate</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
<div class="notice"><strong>Interpretation boundary</strong><br>This report describes structural data-quality signals. It does not modify the source file or infer business or scientific conclusions.</div>
</main></body></html>
"""


def write_report_bundle(summary: dict, output: str | Path) -> dict[str, Path]:
    """Write machine-readable and human-readable reports to one directory."""
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_path / "summary.json",
        "markdown": output_path / "report.md",
        "html": output_path / "report.html",
    }
    paths["json"].write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    paths["markdown"].write_text(_markdown(summary), encoding="utf-8")
    paths["html"].write_text(_html(summary), encoding="utf-8")
    return paths
