from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.local_env import load_env_file


class LocalEnvironmentTests(unittest.TestCase):
    def test_loads_plain_exported_and_quoted_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text(
                "PLAIN=value\n"
                "export EXPORTED='two words'\n"
                'DOUBLE_QUOTED="quoted"\n',
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                load_env_file(path)
                self.assertEqual(os.environ["PLAIN"], "value")
                self.assertEqual(os.environ["EXPORTED"], "two words")
                self.assertEqual(os.environ["DOUBLE_QUOTED"], "quoted")

    def test_does_not_override_terminal_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text("CAS_API_PORT=8081\n", encoding="utf-8")
            with patch.dict(os.environ, {"CAS_API_PORT": "9090"}, clear=True):
                load_env_file(path)
                self.assertEqual(os.environ["CAS_API_PORT"], "9090")

    def test_rejects_malformed_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text("NOT AN ASSIGNMENT\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_env_file(path)


if __name__ == "__main__":
    unittest.main()
