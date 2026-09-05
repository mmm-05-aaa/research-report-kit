import json
import tempfile
import unittest
from pathlib import Path

from reportkit.core import summarize_csv, write_summary


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


if __name__ == "__main__":
    unittest.main()

