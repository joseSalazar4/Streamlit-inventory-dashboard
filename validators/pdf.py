from __future__ import annotations

import io
import re
import time
import unicodedata
from typing import Any, Dict, List, Tuple

import streamlit as st

from document_storage import prepare_document
from models.file_rule import FileRule


class PdfExtractionError(RuntimeError):
    pass


def safe_ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower().strip() if "." in name else ""


def _bytes_to_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader
            from PyPDF2.errors import PdfReadError
        except ModuleNotFoundError as exc:
            raise PdfExtractionError("Missing PDF reader dependency. Install requirements.txt.") from exc

    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
    except PdfReadError as exc:
        raise PdfExtractionError("The file is not a valid PDF.") from exc
    except Exception as exc:
        raise PdfExtractionError(f"Could not open the PDF ({type(exc).__name__}).") from exc

    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception:
            unlocked = 0
        if not unlocked:
            raise PdfExtractionError("The PDF is password protected.")

    extracted_parts: List[str] = []
    page_errors: List[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            if text:
                extracted_parts.append(text)
        except Exception as exc:
            page_errors.append(f"page {page_number}: {type(exc).__name__}")

    try:
        form_fields = reader.get_fields() or {}
        for field_name, field_data in form_fields.items():
            value = field_data.get("/V")
            if value not in (None, ""):
                extracted_parts.append(f"{field_name}: {value}")
    except Exception:
        pass

    if not extracted_parts and page_errors:
        raise PdfExtractionError("Could not extract text from the PDF (" + "; ".join(page_errors) + ").")

    return "\n".join(extracted_parts)


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("_", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return value


def _field_label_pattern(field: str) -> str:
    words = re.findall(r"[a-z0-9]+", _normalize_text(field))
    separator = r"[\s_-]+(?:(?:de|del|la|el)[\s_-]+)?"
    patterns = []
    for word in words:
        plural_suffix = "" if word.endswith("s") else "s?"
        patterns.append(re.escape(word) + plural_suffix)
    return separator.join(patterns)


def _has_filled_field(text: str, field: str, all_fields: List[str]) -> bool:
    normalized = _normalize_text(text)
    field_pattern = _field_label_pattern(field)
    other_labels = [
        _field_label_pattern(other)
        for other in all_fields
        if _normalize_text(other) != _normalize_text(field)
    ]
    stop_pattern = "|".join(other_labels)
    lookahead = rf"(?=\n|{stop_pattern}\s*[:\-]|\Z)" if stop_pattern else r"(?=\n|\Z)"
    pattern = re.compile(
        rf"\b{field_pattern}\b\s*(?:[:=\-]\s*)?(.*?){lookahead}",
        re.IGNORECASE,
    )

    for match in pattern.finditer(normalized):
        candidate = match.group(1).strip()
        candidate = re.sub(r"^[.\-:/\\\s]+|[.\-:/\\\s]+$", "", candidate)
        if re.search(r"[a-z0-9]", candidate):
            return True
    return False


def validate_pdf(file_name: str, data: bytes, rule: FileRule) -> Tuple[bool, str]:
    ext = safe_ext(file_name)
    if ext != "pdf":
        return False, f".{ext or 'no extension'} files are not allowed. Upload a PDF."

    try:
        text = _bytes_to_text(data)
        if not text.strip():
            return False, "No selectable text was found. Scanned PDFs require OCR."
        if not rule.required_fields:
            return True, "PDF is valid and readable."

        missing = [
            field
            for field in rule.required_fields
            if not _has_filled_field(text, field, rule.required_fields)
        ]
        if missing:
            return False, f"Missing or empty fields: {', '.join(missing)}"
        return True, f"PDF is valid. Completed fields: {', '.join(rule.required_fields)}"
    except PdfExtractionError as exc:
        return False, str(exc)


def uploader_key(stage_id: int, rule_key: str) -> str:
    return f"u_{stage_id}_{rule_key}"


def validation_key(stage_id: int, rule_key: str) -> Tuple[int, str]:
    return stage_id, rule_key


def process_uploaded_file(stage_id: int, rule: FileRule) -> None:
    widget_key = uploader_key(stage_id, rule.key)
    result_key = validation_key(stage_id, rule.key)
    uploaded_file = st.session_state.get(widget_key)

    if uploaded_file is None:
        st.session_state.validation.pop(result_key, None)
        st.session_state.pending_uploads.pop(result_key, None)
        return

    data = uploaded_file.getvalue()
    document = prepare_document(
        stage_id=stage_id,
        document_key=rule.key,
        file_name=uploaded_file.name,
        content_type=getattr(uploaded_file, "type", None) or "application/pdf",
        data=data,
    )
    st.session_state.pending_uploads[result_key] = document
    st.session_state.validation[result_key] = {
        "ok": None,
        "message": "Preparing PDF...",
        "file_name": document.file_name,
        "file_size": document.size,
        "sha256": document.sha256,
        "progress": 10,
        "processing": True,
        "storage_status": "processing",
    }


def finish_uploaded_file(
    stage_id: int,
    rule: FileRule,
    progress_bar,
) -> Dict[str, Any]:
    result_key = validation_key(stage_id, rule.key)
    document = st.session_state.pending_uploads[result_key]
    steps = [
        (25, "Uploading file..."),
        (45, "Reading PDF..."),
        (65, "Checking required fields..."),
        (85, "Verifying information..."),
    ]

    for progress, label in steps:
        progress_bar.progress(progress, text=label)
        time.sleep(0.85)

    ok, message = validate_pdf(document.file_name, document.data, rule)
    result = st.session_state.validation[result_key]
    result.update(
        {
            "ok": ok,
            "message": message,
            "progress": 100,
            "processing": False,
            "storage_status": "ready" if ok else "blocked",
        }
    )
    progress_bar.progress(100, text="File ready" if ok else "Review complete")
    return result
