import tempfile
import unittest
from pathlib import Path

from reportkit.gui import generate_report


class GuiControllerTests(unittest.TestCase):
    def test_generate_report_returns_html_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            output = root / "output"
            original = b"name,value\nalpha,1\nbeta,\n"
            source.write_bytes(original)
            result = generate_report(source, output)
            self.assertEqual(result, output / "report.html")
            self.assertTrue(result.is_file())
            self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
