import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from reportkit.cli import main


class CliTests(unittest.TestCase):
    def test_inspect_writes_complete_report_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "data.csv"
            output = root / "report"
            source.write_text("item,amount\nA,10\nB,\n", encoding="utf-8")
            stdout = StringIO()
            with redirect_stdout(stdout):
                status = main(["inspect", str(source), "--out", str(output), "--json"])
            self.assertEqual(status, 0)
            self.assertTrue((output / "summary.json").is_file())
            self.assertTrue((output / "report.md").is_file())
            self.assertTrue((output / "report.html").is_file())
            self.assertEqual(json.loads((output / "summary.json").read_text(encoding="utf-8"))["rows"], 2)
            self.assertIn("Wrote 3 report files", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
