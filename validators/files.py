from __future__ import annotations

import logging
import mimetypes
from typing import Any, Dict, Tuple

import streamlit as st

from api.cas_api import (
    CasApiError,
    StudentFileUpload,
    get_admission_progress,
    upload_student_files,
)
from document_storage import prepare_document
from models.file_rule import FileRule
from validators.file_content import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE_BYTES,
    safe_ext,
    validate_file,
)

LOGGER = logging.getLogger(__name__)


def uploader_key(phase_id: str, rule_key: str) -> str:
    return f"u_{phase_id}_{rule_key}"


def validation_key(phase_id: str, rule_key: str) -> Tuple[str, str]:
    return phase_id, rule_key


def process_uploaded_file(phase_id: str, rule: FileRule) -> None:
    result_key = validation_key(phase_id, rule.key)
    uploaded_file = st.session_state.get(uploader_key(phase_id, rule.key))
    if uploaded_file is None:
        st.session_state.validation.pop(result_key, None)
        st.session_state.pending_uploads.pop(result_key, None)
        return

    data = uploaded_file.getvalue()
    ok, message = validate_file(uploaded_file.name, data)
    if not ok:
        st.session_state.pending_uploads.pop(result_key, None)
        st.session_state.validation[result_key] = {
            "ok": False,
            "message": message,
            "file_name": uploaded_file.name,
            "file_size": len(data),
            "storage_status": "blocked",
        }
        return

    content_type = (
        getattr(uploaded_file, "type", None)
        or mimetypes.guess_type(uploaded_file.name)[0]
        or "application/octet-stream"
    )
    document = prepare_document(
        phase_id=phase_id,
        document_type_id=rule.key,
        file_name=uploaded_file.name,
        content_type=content_type,
        data=data,
    )
    st.session_state.pending_uploads[result_key] = document
    st.session_state.validation[result_key] = {
        "ok": True,
        "message": f"{message} Ready to submit.",
        "file_name": document.file_name,
        "file_size": document.size,
        "sha256": document.sha256,
        "storage_status": "ready_to_submit",
    }


def submit_uploaded_files(
    phase_id: str,
    rules: list[FileRule],
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    user = st.session_state.get("authenticated_user") or {}
    student_id = str(user.get("student_id") or "").strip()
    if not student_id:
        raise ValueError("Your account is missing required information. Contact support.")

    results: Dict[Tuple[str, str], Dict[str, Any]] = {}
    prepared: list[Tuple[Tuple[str, str], StudentFileUpload]] = []
    for rule in rules:
        result_key = validation_key(phase_id, rule.key)
        result = st.session_state.validation.get(result_key)
        document = st.session_state.pending_uploads.get(result_key)
        if not result or not result.get("ok") or document is None:
            raise ValueError(f"Choose a valid file for {rule.label} before submitting.")
        results[result_key] = result
        if result.get("storage_status") == "saved":
            continue
        result["storage_status"] = "submitting"
        prepared.append(
            (
                result_key,
                StudentFileUpload(
                    student_id=student_id,
                    document_type_id=document.document_type_id,
                    file_name=document.file_name,
                    content=document.data,
                    content_type=document.content_type,
                ),
            )
        )

    outcomes = upload_student_files([upload for _, upload in prepared])
    saved_any = False
    for (result_key, _), outcome in zip(prepared, outcomes):
        result = results[result_key]
        if outcome.error is not None:
            LOGGER.warning(
                "File submission failed for %s/%s: %s",
                phase_id,
                result_key[1],
                outcome.error,
            )
            result.update(
                {
                    "ok": True,
                    "message": "File could not be submitted. Please try again.",
                    "storage_status": "ready_to_submit",
                }
            )
            continue

        response = outcome.response or {}
        result.update(
            {
                "ok": True,
                "message": "File submitted.",
                "storage_status": "saved",
                "document_id": response.get("document_id"),
                "version": response.get("version"),
            }
        )
        st.session_state.pending_uploads.pop(result_key, None)
        saved_any = True

    if saved_any:
        try:
            st.session_state.admission_progress = get_admission_progress(student_id)
        except CasApiError:
            pass
    return results


def submit_uploaded_file(phase_id: str, rule: FileRule) -> Dict[str, Any]:
    return submit_uploaded_files(phase_id, [rule])[validation_key(phase_id, rule.key)]
