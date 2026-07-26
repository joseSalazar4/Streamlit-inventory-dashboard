from __future__ import annotations

import unittest
from unittest.mock import patch

from validators.files import MAX_FILE_SIZE_BYTES, validate_file


class FileValidationTests(unittest.TestCase):
    def test_accepts_supported_file_signatures(self) -> None:
        samples = {
            "document.pdf": b"%PDF-1.7\ncontent\n%%EOF",
            "photo.jpg": b"\xff\xd8\xff\xe0content\xff\xd9",
            "photo.jpeg": b"\xff\xd8\xff\xe1content\xff\xd9",
            "image.png": b"\x89PNG\r\n\x1a\ncontentIEND\xaeB`\x82",
        }
        for name, content in samples.items():
            with self.subTest(name=name):
                ok, message = validate_file(name, content)
                self.assertTrue(ok)
                self.assertEqual(message, "File selected.")

    def test_rejects_disallowed_extension_and_mismatched_content(self) -> None:
        self.assertFalse(validate_file("malware.exe", b"MZ")[0])
        self.assertFalse(validate_file("malware.pdf", b"MZ")[0])
        self.assertFalse(validate_file("malware.png", b"<script>")[0])

    def test_rejects_pdf_active_content(self) -> None:
        ok, message = validate_file(
            "scripted.pdf",
            b"%PDF-1.7\n1 0 obj <</OpenAction 2 0 R>>\n%%EOF",
        )
        self.assertFalse(ok)
        self.assertEqual(
            message,
            "This PDF contains unsupported content. Please choose a different file.",
        )

    @patch("validators.file_content.MAX_FILE_SIZE_BYTES", 8)
    def test_rejects_file_over_configured_limit(self) -> None:
        ok, message = validate_file("large.pdf", b"%PDF" + b"x" * 5 + b"%%EOF")
        self.assertFalse(ok)
        self.assertIn("40 MB", message)

    def test_limit_is_40_mib(self) -> None:
        self.assertEqual(MAX_FILE_SIZE_BYTES, 40 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
