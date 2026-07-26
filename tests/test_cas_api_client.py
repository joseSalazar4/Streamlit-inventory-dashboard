from __future__ import annotations

import json
import threading
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from api.cas_api import (
    CasApiError,
    StudentFileUpload,
    _api_error,
    authenticate_student,
    change_password,
    document_download_url,
    document_template_download_url,
    request_password_reset,
    upload_student_file,
    upload_student_files,
)
from app_pages.auth import _student_from_login


def response(payload: dict) -> Mock:
    value = Mock()
    value.__enter__ = Mock(return_value=value)
    value.__exit__ = Mock(return_value=False)
    value.read.return_value = json.dumps(payload).encode("utf-8")
    return value


class CasApiClientTests(unittest.TestCase):
    @patch.dict("os.environ", {"CAS_TEST_STUDENT_ID": ""}, clear=False)
    @patch("app_pages.auth.authenticate_student")
    def test_test_login_is_disabled_without_an_explicit_student(
        self,
        authenticate: Mock,
    ) -> None:
        authenticate.side_effect = CasApiError("Invalid credentials.", status=401)

        with self.assertRaises(CasApiError):
            _student_from_login("admin", "admin")

        authenticate.assert_called_once_with("admin", "admin")

    @patch.dict("os.environ", {"CAS_TEST_STUDENT_ID": "EST-TEST"}, clear=False)
    @patch("app_pages.auth.authenticate_student")
    @patch("app_pages.auth.get_admission_progress")
    def test_test_login_requires_an_explicit_student(
        self,
        get_progress: Mock,
        authenticate: Mock,
    ) -> None:
        get_progress.return_value = {"student": {"student_id": "EST-TEST"}}

        user, progress = _student_from_login("admin", "admin")

        self.assertEqual(user["student_id"], "EST-TEST")
        self.assertTrue(user["is_test_user"])
        self.assertEqual(progress, get_progress.return_value)
        authenticate.assert_not_called()

    @patch.dict("os.environ", {"CAS_API_BASE_URL": "http://api.test"}, clear=False)
    @patch("api.cas_api.request.urlopen")
    def test_authentication_uses_student_login_endpoint(self, urlopen: Mock) -> None:
        urlopen.return_value = response({"user": {"user_type": "student"}})
        payload = authenticate_student("Ana@Example.com", "secret")
        sent = urlopen.call_args.args[0]

        self.assertEqual(sent.full_url, "http://api.test/auth/login")
        self.assertEqual(json.loads(sent.data), {"email": "ana@example.com", "password": "secret"})
        self.assertEqual(payload["user"]["user_type"], "student")

    @patch.dict("os.environ", {"CAS_API_BASE_URL": "http://api.test"}, clear=False)
    @patch("api.cas_api.request.urlopen")
    def test_password_reset_client_uses_auth_endpoints(self, urlopen: Mock) -> None:
        urlopen.return_value = response({"message": "ok"})

        request_password_reset("Ana@Example.com")
        reset_request = urlopen.call_args.args[0]
        self.assertEqual(
            reset_request.full_url,
            "http://api.test/auth/forgot-password",
        )
        self.assertEqual(
            json.loads(reset_request.data),
            {"email": "ana@example.com"},
        )

        change_password("Ana@Example.com", "signed-token", "NewPassword1")
        change_request = urlopen.call_args.args[0]
        self.assertEqual(
            change_request.full_url,
            "http://api.test/auth/change-password",
        )
        self.assertEqual(
            json.loads(change_request.data),
            {
                "email": "ana@example.com",
                "change_token": "signed-token",
                "new_password": "NewPassword1",
            },
        )

    @patch.dict("os.environ", {"CAS_API_BASE_URL": "http://api.test"}, clear=False)
    @patch("api.cas_api.request.urlopen")
    def test_student_upload_uses_contract_route_and_multipart_body(self, urlopen: Mock) -> None:
        urlopen.return_value = response({"document_id": "DOC-1", "version": 2})
        payload = upload_student_file(
            "EST-1",
            "agbs",
            "signed.pdf",
            b"%PDF-1.7",
            "application/pdf",
        )
        sent = urlopen.call_args.args[0]

        self.assertEqual(
            sent.full_url,
            "http://api.test/students/EST-1/documents/agbs/student-file",
        )
        self.assertIn(b'filename="signed.pdf"', sent.data)
        self.assertIn(b"%PDF-1.7", sent.data)
        self.assertEqual(payload["version"], 2)

    @patch.dict("os.environ", {"CAS_API_BASE_URL": "http://api.test"}, clear=False)
    def test_download_routes_point_to_api(self) -> None:
        self.assertEqual(
            document_download_url("DOC 1"),
            "http://api.test/documents/DOC%201/download",
        )
        self.assertEqual(
            document_template_download_url("reglas_programa"),
            "http://api.test/document-templates/reglas_programa/download?scope=global",
        )

    def test_aborted_error_body_is_reported_as_api_error(self) -> None:
        error = HTTPError(
            "http://api.test/documents/upload",
            500,
            "Internal Server Error",
            {},
            None,
        )
        error.read = Mock(side_effect=ConnectionAbortedError(10053, "aborted"))

        result = _api_error(error)

        self.assertIsInstance(result, CasApiError)
        self.assertEqual(result.status, 500)
        self.assertIn("HTTP 500", result.message)

    def test_batch_upload_uses_one_thread_per_file_and_preserves_order(self) -> None:
        uploads = [
            StudentFileUpload(
                student_id="EST-1",
                document_type_id=f"document-{index}",
                file_name=f"file-{index}.pdf",
                content=b"%PDF-1.7\n%%EOF",
                content_type="application/pdf",
            )
            for index in range(3)
        ]
        barrier = threading.Barrier(len(uploads))
        thread_ids: set[int] = set()
        lock = threading.Lock()

        def concurrent_upload(**kwargs):
            with lock:
                thread_ids.add(threading.get_ident())
            barrier.wait(timeout=5)
            return {
                "document_id": kwargs["document_type_id"],
                "version": 1,
            }

        with patch("api.cas_api.upload_student_file", side_effect=concurrent_upload):
            outcomes = upload_student_files(uploads)

        self.assertEqual(len(thread_ids), len(uploads))
        self.assertEqual(
            [outcome.response["document_id"] for outcome in outcomes],
            ["document-0", "document-1", "document-2"],
        )
        self.assertTrue(all(outcome.error is None for outcome in outcomes))

    def test_batch_upload_keeps_individual_file_errors(self) -> None:
        uploads = [
            StudentFileUpload("EST-1", "good", "good.pdf", b"good"),
            StudentFileUpload("EST-1", "bad", "bad.pdf", b"bad"),
        ]

        def upload_with_failure(**kwargs):
            if kwargs["document_type_id"] == "bad":
                raise CasApiError("Rejected", status=400, code="bad_request")
            return {"document_id": "DOC-1", "version": 1}

        with patch("api.cas_api.upload_student_file", side_effect=upload_with_failure):
            outcomes = upload_student_files(uploads)

        self.assertEqual(outcomes[0].response["document_id"], "DOC-1")
        self.assertIsNone(outcomes[0].error)
        self.assertIsNone(outcomes[1].response)
        self.assertEqual(outcomes[1].error.code, "bad_request")


if __name__ == "__main__":
    unittest.main()
