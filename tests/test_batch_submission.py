from __future__ import annotations

import unittest
from unittest.mock import patch

from api.cas_api import (
    CasApiError,
    StudentFileUpload,
    StudentFileUploadOutcome,
)
from document_storage import prepare_document
from models.file_rule import FileRule
from validators.files import submit_uploaded_files, validation_key


class FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def rule(key: str) -> FileRule:
    return FileRule(
        key=key,
        label=key,
        description="",
        flow_type="student_upload_review",
        template_scope="none",
        can_student_upload=True,
        requires_review=True,
    )


class BatchSubmissionTests(unittest.TestCase):
    def test_batch_updates_state_once_and_retains_only_failed_file(self) -> None:
        first_rule = rule("first")
        second_rule = rule("second")
        first_key = validation_key("phase", "first")
        second_key = validation_key("phase", "second")
        first_document = prepare_document(
            "phase",
            "first",
            "first.pdf",
            "application/pdf",
            b"%PDF-1.7\n%%EOF",
        )
        second_document = prepare_document(
            "phase",
            "second",
            "second.pdf",
            "application/pdf",
            b"%PDF-1.7\n%%EOF",
        )
        state = FakeSessionState(
            authenticated_user={"student_id": "EST-1"},
            validation={
                first_key: {"ok": True, "storage_status": "ready_to_submit"},
                second_key: {"ok": True, "storage_status": "ready_to_submit"},
            },
            pending_uploads={
                first_key: first_document,
                second_key: second_document,
            },
            admission_progress=None,
        )

        outcomes = [
            StudentFileUploadOutcome(
                upload=StudentFileUpload(
                    "EST-1",
                    "first",
                    "first.pdf",
                    first_document.data,
                    first_document.content_type,
                ),
                response={"document_id": "DOC-1", "version": 1},
            ),
            StudentFileUploadOutcome(
                upload=StudentFileUpload(
                    "EST-1",
                    "second",
                    "second.pdf",
                    second_document.data,
                    second_document.content_type,
                ),
                error=CasApiError("Rejected", status=400),
            ),
        ]
        with (
            patch("validators.files.st.session_state", state),
            patch("validators.files.upload_student_files", return_value=outcomes) as upload_batch,
            patch(
                "validators.files.get_admission_progress",
                return_value={"student": {"student_id": "EST-1"}},
            ) as refresh_progress,
        ):
            results = submit_uploaded_files("phase", [first_rule, second_rule])

        upload_batch.assert_called_once()
        self.assertEqual(len(upload_batch.call_args.args[0]), 2)
        refresh_progress.assert_called_once_with("EST-1")
        self.assertEqual(results[first_key]["storage_status"], "saved")
        self.assertEqual(results[second_key]["storage_status"], "ready_to_submit")
        self.assertEqual(results[first_key]["message"], "File submitted.")
        self.assertEqual(
            results[second_key]["message"],
            "File could not be submitted. Please try again.",
        )
        self.assertNotIn("CAS API", results[second_key]["message"])
        self.assertNotIn("Rejected", results[second_key]["message"])
        self.assertNotIn(first_key, state.pending_uploads)
        self.assertIn(second_key, state.pending_uploads)


if __name__ == "__main__":
    unittest.main()
