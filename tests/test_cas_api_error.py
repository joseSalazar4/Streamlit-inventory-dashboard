import unittest
from contextlib import contextmanager
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.cas_api import CasApiError


@contextmanager
def streamlit_style_context_manager():
    yield


class CasApiErrorTests(unittest.TestCase):
    def test_error_can_cross_context_manager_without_frozen_traceback_failure(self) -> None:
        with self.assertRaises(CasApiError) as raised:
            with streamlit_style_context_manager():
                raise CasApiError("API unavailable", status=502, code="api_unavailable")

        self.assertEqual(str(raised.exception), "API unavailable")
        self.assertEqual(raised.exception.status, 502)


if __name__ == "__main__":
    unittest.main()
