import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
from campusflow.storage import StorageError


class MainTests(unittest.TestCase):
    def test_startup_load_failure_exits_without_showing_menu(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "tickets.json"
            output = StringIO()

            with (
                patch(
                    "main.parse_args",
                    return_value=SimpleNamespace(data=data_path),
                ),
                patch(
                    "main.load_tickets",
                    side_effect=StorageError("invalid JSON"),
                ),
                patch("main.print_menu") as mock_print_menu,
                redirect_stdout(output),
            ):
                result = main.main()

            self.assertEqual(result, 1)
            mock_print_menu.assert_not_called()
            self.assertIn("Startup error:", output.getvalue())
            self.assertIn(
                "Fix or restore the data file",
                output.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()