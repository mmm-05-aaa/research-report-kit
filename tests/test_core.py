import json
import tempfile
import unittest
from pathlib import Path

from reportkit.core import summarize_csv, write_report_bundle, write_summary


class SummaryTests(unittest.TestCase):
    def test_summary_reports_types_missing_and_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("id,score,note\n1,2.5,a\n1,2.5,a\n2,,b\n", encoding="utf-8")
            summary = summarize_csv(source)
            self.assertEqual(summary["rows"], 3)
            self.assertEqual(summary["columns"], 3)
            self.assertEqual(summary["missing_values"], 1)
            self.assertEqual(summary["duplicate_rows"], 1)
            self.assertEqual(summary["column_summary"][1]["type"], "numeric")
            self.assertEqual(summary["column_summary"][1]["statistics"]["median"], 2.5)

    def test_summary_can_be_written_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("id\n1\n", encoding="utf-8")
            target = write_summary(summarize_csv(source), Path(directory) / "out")
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["rows"], 1)

    def test_multiline_quoted_field_is_one_record(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text('id,note\n1,"first line\nsecond line"\n2,plain\n', encoding="utf-8")
            summary = summarize_csv(source)
            self.assertEqual(summary["rows"], 2)
            self.assertEqual(summary["irregular_rows"], 0)

    def test_non_finite_values_are_not_numeric_statistics(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("value\ninf\n1\n", encoding="utf-8")
            summary = summarize_csv(source)
            self.assertEqual(summary["column_summary"][0]["type"], "text")

    def test_common_missing_markers_do_not_turn_numeric_column_into_text(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("value\n1\nNA\nNaN\n3\n", encoding="utf-8")
            summary = summarize_csv(source)
            self.assertEqual(summary["missing_values"], 2)
            self.assertEqual(summary["column_summary"][0]["type"], "numeric")
            self.assertEqual(summary["column_summary"][0]["missing"], 2)

    def test_malformed_unclosed_quote_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "malformed.csv"
            source.write_text('id,note\n1,"unclosed\n2,value\n', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Malformed CSV"):
                summarize_csv(source)

    def test_report_bundle_writes_json_markdown_and_safe_html(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text('<script>,score\nhello,3\n,5\n', encoding="utf-8")
            output = Path(directory) / "report"
            paths = write_report_bundle(summarize_csv(source), output)
            self.assertEqual(set(paths), {"json", "markdown", "html"})
            self.assertTrue((output / "summary.json").is_file())
            self.assertIn("Data quality overview", (output / "report.md").read_text(encoding="utf-8"))
            html = (output / "report.html").read_text(encoding="utf-8")
            self.assertIn("&lt;script&gt;", html)
            self.assertNotIn("<script>", html)

    def test_summary_has_source_hash_and_structural_issues(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("id,id,\n1,2\n3,4,5,6\n", encoding="utf-8")
            summary = summarize_csv(source)
            self.assertEqual(len(summary["source_sha256"]), 64)
            self.assertEqual(
                summary["issues"],
                ["duplicate_header_labels", "empty_header_labels", "irregular_row_widths"],
            )
            output = Path(directory) / "report"
            write_report_bundle(summary, output)
            self.assertIn("duplicate_header_labels", (output / "report.md").read_text(encoding="utf-8"))
            self.assertIn("duplicate_header_labels", (output / "report.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

