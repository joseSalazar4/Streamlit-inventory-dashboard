from __future__ import annotations

import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock, patch
from urllib import request
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_API = ROOT / ".local" / "cas-document-platform" / "cas-api"
UPSTREAM_API_AVAILABLE = (UPSTREAM_API / "cas_api" / "server.py").is_file()

if UPSTREAM_API_AVAILABLE:
    sys.path.insert(0, str(UPSTREAM_API))
    from local_api.student_upload_server import (
        StudentUploadApiHandler,
        StudentUploadDataverseClient,
        _student_document_type_from_path,
    )


@unittest.skipUnless(UPSTREAM_API_AVAILABLE, "Local CAS API checkout is not available.")
class StudentUploadApiTests(unittest.TestCase):
    def test_both_contract_routes_are_registered(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), StudentUploadApiHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for path in (
                "/documents/upload",
                "/students/EST-1/documents/agbs/student-file",
            ):
                with self.subTest(path=path):
                    api_request = request.Request(
                        f"http://127.0.0.1:{server.server_port}{path}",
                        data=b"{}",
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self.assertRaises(HTTPError) as raised:
                        request.urlopen(api_request, timeout=5)
                    payload = json.loads(raised.exception.read())
                    self.assertEqual(raised.exception.code, 400)
                    self.assertEqual(payload["error"]["code"], "bad_request")
                    self.assertNotEqual(payload["error"]["code"], "not_found")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_path_route_extracts_student_and_document_type(self) -> None:
        self.assertEqual(
            _student_document_type_from_path(
                "/students/EST%201/documents/passport/student-file"
            ),
            ("EST 1", "passport"),
        )

    def test_valid_student_file_reaches_sharepoint_and_dataverse(self) -> None:
        dataverse = Mock()
        dataverse.prepare_student_file_upload.return_value = 2
        dataverse.upsert_student_file_reference.return_value = {
            "document_id": "DOC-1",
            "student_id": "EST-1",
            "document_type_id": "passport",
            "status": "pending_review",
            "version": 2,
            "file_name": "passport.pdf",
        }
        sharepoint = Mock()
        sharepoint.upload_admission_file.return_value = {
            "id": "ITEM-1",
            "webUrl": "https://sharepoint/Admissions/EST-1/passport/2/passport.pdf",
            "name": "passport.pdf",
        }
        boundary = "----cas-test"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="passport.pdf"\r\n'
            "Content-Type: application/pdf\r\n\r\n"
        ).encode("ascii") + b"%PDF-1.7\n%%EOF" + f"\r\n--{boundary}--\r\n".encode("ascii")

        with (
            patch(
                "local_api.student_upload_server.StudentUploadDataverseClient",
                return_value=dataverse,
            ),
            patch(
                "local_api.student_upload_server.SharePointClient",
                return_value=sharepoint,
            ),
        ):
            server = ThreadingHTTPServer(("127.0.0.1", 0), StudentUploadApiHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                api_request = request.Request(
                    (
                        f"http://127.0.0.1:{server.server_port}"
                        "/students/EST-1/documents/passport/student-file"
                    ),
                    data=body,
                    headers={
                        "Content-Type": f"multipart/form-data; boundary={boundary}"
                    },
                    method="POST",
                )
                with request.urlopen(api_request, timeout=5) as response:
                    payload = json.loads(response.read())
                self.assertEqual(response.status, 201)
                self.assertEqual(payload["document_id"], "DOC-1")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        dataverse.prepare_student_file_upload.assert_called_once_with(
            "EST-1",
            "passport",
            "passport.pdf",
        )
        sharepoint.upload_admission_file.assert_called_once()
        dataverse.upsert_student_file_reference.assert_called_once()

    def test_prepare_upload_checks_permission_extension_and_version(self) -> None:
        client = StudentUploadDataverseClient(Mock())
        client.get_student = Mock(return_value={"student_id": "EST-1"})
        client.list_document_types = Mock(
            return_value=[
                {
                    "document_type_id": "passport",
                    "can_student_upload": True,
                    "allowed_file_types": ["pdf", "jpg"],
                }
            ]
        )
        client.list_student_documents = Mock(
            return_value=[
                {
                    "document_type_id": "passport",
                    "sharepoint_web_url": "https://sharepoint/Admissions/EST-1/passport/2/old.pdf",
                }
            ]
        )

        self.assertEqual(
            client.prepare_student_file_upload("EST-1", "passport", "new.pdf"),
            3,
        )
        with self.assertRaisesRegex(ValueError, "does not allow"):
            client.prepare_student_file_upload("EST-1", "passport", "new.png")

    def test_upsert_marks_reviewable_student_file_pending(self) -> None:
        client = StudentUploadDataverseClient(Mock())
        student = {"student_id": "EST-1"}
        document_type = {
            "document_type_id": "passport",
            "can_student_upload": True,
            "requires_review": True,
        }
        client._student_upload_context = Mock(
            return_value=(student, document_type, None)
        )
        client._set_student_reference = Mock()
        client._set_document_type_reference = Mock()
        client._create_row = Mock()

        result = client.upsert_student_file_reference(
            "EST-1",
            "passport",
            "ITEM-1",
            "https://sharepoint/Admissions/EST-1/passport/1/passport.pdf",
            "passport.pdf",
        )

        self.assertEqual(result["status"], "pending_review")
        self.assertEqual(result["version"], 1)
        self.assertTrue(result["student_file_available"])
        client._create_row.assert_called_once()


if __name__ == "__main__":
    unittest.main()
