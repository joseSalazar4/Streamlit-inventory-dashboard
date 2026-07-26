from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from api.cas_api import CasApiError
from app_pages.dashboard import _load_progress


class DashboardProgressTests(unittest.TestCase):
    @patch("app_pages.dashboard.get_admission_progress")
    @patch("app_pages.dashboard.st")
    def test_dashboard_refreshes_progress_after_cas_approval(
        self,
        streamlit: Mock,
        get_progress: Mock,
    ) -> None:
        cached = {"student": {"current_phase_id": "contrato"}}
        refreshed = {
            "student": {"current_phase_id": "documentos_complementarios"},
        }
        streamlit.session_state = {
            "authenticated_user": {"student_id": "EST-1"},
            "admission_progress": cached,
        }
        get_progress.return_value = refreshed

        self.assertEqual(_load_progress(), refreshed)
        self.assertEqual(streamlit.session_state["admission_progress"], refreshed)
        get_progress.assert_called_once_with("EST-1")

    @patch("app_pages.dashboard.get_admission_progress")
    @patch("app_pages.dashboard.st")
    def test_dashboard_keeps_cached_progress_if_refresh_fails(
        self,
        streamlit: Mock,
        get_progress: Mock,
    ) -> None:
        cached = {"student": {"current_phase_id": "contrato"}}
        streamlit.session_state = {
            "authenticated_user": {"student_id": "EST-1"},
            "admission_progress": cached,
        }
        get_progress.side_effect = CasApiError("Unavailable", status=503)

        self.assertEqual(_load_progress(), cached)


if __name__ == "__main__":
    unittest.main()
