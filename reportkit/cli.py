import argparse
import json
from pathlib import Path

from . import __version__
from .core import summarize_csv, write_report_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reportkit", description="Create local-first CSV quality reports in JSON, Markdown and HTML.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="inspect a CSV and write a complete report bundle")
    inspect.add_argument("source", type=Path, help="path to a CSV file")
    inspect.add_argument("--out", type=Path, default=Path("report"), help="output directory (default: report)")
    inspect.add_argument("--json", action="store_true", help="also print the summary as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        try:
            summary = summarize_csv(args.source)
            targets = write_report_bundle(summary, args.out)
        except (OSError, ValueError) as error:
            print(f"error: {error}")
            return 2
        print(f"Wrote {len(targets)} report files to {args.out}")
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

