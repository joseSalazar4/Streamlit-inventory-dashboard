from __future__ import annotations

import json
import mimetypes
import os
import socket
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, Mapping
from urllib import parse, request
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class CasApiError(RuntimeError):
    message: str
    status: int | None = None
    code: str = ""

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class StudentFileUpload:
    student_id: str
    document_type_id: str
    file_name: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass(frozen=True)
class StudentFileUploadOutcome:
    upload: StudentFileUpload
    response: Dict[str, Any] | None = None
    error: CasApiError | None = None


def api_base_url() -> str:
    return os.getenv("CAS_API_BASE_URL", "http://127.0.0.1:8080").rstrip("/")


def authenticate_student(email: str, password: str) -> Dict[str, Any]:
    return _request_json(
        "POST",
        "/auth/login",
        payload={"email": email.strip().lower(), "password": password},
    )


def request_password_reset(email: str) -> Dict[str, Any]:
    return _request_json(
        "POST",
        "/auth/forgot-password",
        payload={"email": email.strip().lower()},
    )


def change_password(
    email: str,
    change_token: str,
    new_password: str,
) -> Dict[str, Any]:
    return _request_json(
        "POST",
        "/auth/change-password",
        payload={
            "email": email.strip().lower(),
            "change_token": change_token,
            "new_password": new_password,
        },
    )


def get_student_by_email(email: str) -> Dict[str, Any] | None:
    normalized = email.strip().lower()
    query = parse.urlencode({"search": normalized})
    payload = _request_json("GET", f"/dashboard/documents?{query}")
    for student in payload.get("students", []):
        if str(student.get("email") or "").strip().lower() == normalized:
            return dict(student)
    return None


def get_admission_progress(student_id: str) -> Dict[str, Any]:
    encoded = parse.quote(str(student_id), safe="")
    return _request_json("GET", f"/students/{encoded}/admission-progress")


def upload_student_file(
    student_id: str,
    document_type_id: str,
    file_name: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> Dict[str, Any]:
    student = parse.quote(str(student_id), safe="")
    document_type = parse.quote(document_type_id, safe="")
    try:
        return _post_multipart(
            f"/students/{student}/documents/{document_type}/student-file",
            fields={},
            file_name=file_name,
            content=content,
            content_type=content_type,
        )
    except CasApiError as exc:
        if exc.status != 404:
            raise

    # Compatibility with the resource-oriented upload route in the v1 contract.
    return _post_multipart(
        "/documents/upload",
        fields={
            "student_id": str(student_id),
            "document_type_id": document_type_id,
        },
        file_name=file_name,
        content=content,
        content_type=content_type,
    )


def upload_student_files(
    uploads: list[StudentFileUpload],
) -> list[StudentFileUploadOutcome]:
    """Upload each file in its own worker thread and preserve input order."""
    if not uploads:
        return []

    outcomes: list[StudentFileUploadOutcome | None] = [None] * len(uploads)
    with ThreadPoolExecutor(
        max_workers=len(uploads),
        thread_name_prefix="cas-file-upload",
    ) as executor:
        futures = {
            executor.submit(
                upload_student_file,
                student_id=upload.student_id,
                document_type_id=upload.document_type_id,
                file_name=upload.file_name,
                content=upload.content,
                content_type=upload.content_type,
            ): (index, upload)
            for index, upload in enumerate(uploads)
        }
        for future in as_completed(futures):
            index, upload = futures[future]
            try:
                outcomes[index] = StudentFileUploadOutcome(
                    upload=upload,
                    response=future.result(),
                )
            except CasApiError as exc:
                outcomes[index] = StudentFileUploadOutcome(
                    upload=upload,
                    error=exc,
                )
            except Exception as exc:
                outcomes[index] = StudentFileUploadOutcome(
                    upload=upload,
                    error=CasApiError(f"Upload failed: {exc}"),
                )

    return [outcome for outcome in outcomes if outcome is not None]


def document_download_url(document_id: str) -> str:
    encoded = parse.quote(str(document_id), safe="")
    return f"{api_base_url()}/documents/{encoded}/download"


def document_template_download_url(document_type_id: str, scope: str = "global") -> str:
    encoded = parse.quote(document_type_id, safe="")
    query = parse.urlencode({"scope": scope})
    return f"{api_base_url()}/document-templates/{encoded}/download?{query}"


def download_file(url: str) -> bytes:
    api_request = request.Request(
        url,
        headers={"Accept": "application/octet-stream"},
        method="GET",
    )
    try:
        with request.urlopen(api_request, timeout=150) as response:
            return response.read()
    except HTTPError as exc:
        raise _api_error(exc) from exc
    except (URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise CasApiError(f"The file could not be downloaded: {reason}") from exc


def _request_json(
    method: str,
    path: str,
    payload: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    data = None if payload is None else json.dumps(dict(payload)).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    api_request = request.Request(
        f"{api_base_url()}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(api_request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        raise _api_error(exc) from exc
    except (URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise CasApiError(f"CAS API is not reachable at {api_base_url()}: {reason}") from exc


def _post_multipart(
    path: str,
    fields: Mapping[str, str],
    file_name: str,
    content: bytes,
    content_type: str,
) -> Dict[str, Any]:
    boundary = f"----cas-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    safe_name = os.path.basename(file_name).replace('"', "_")
    resolved_type = content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("ascii"),
            f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'.encode("utf-8"),
            f"Content-Type: {resolved_type}\r\n\r\n".encode("ascii"),
            content,
            f"\r\n--{boundary}--\r\n".encode("ascii"),
        ]
    )
    body = b"".join(chunks)
    api_request = request.Request(
        f"{api_base_url()}{path}",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
        method="POST",
    )
    try:
        with request.urlopen(api_request, timeout=150) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        raise _api_error(exc) from exc
    except (URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise CasApiError(f"CAS API is not reachable at {api_base_url()}: {reason}") from exc


def _api_error(exc: HTTPError) -> CasApiError:
    try:
        raw = exc.read().decode("utf-8", errors="replace")
    except (ConnectionError, OSError):
        raw = ""
    code = ""
    message = raw or f"CAS API returned HTTP {exc.code}."
    try:
        payload = json.loads(raw)
        error = payload.get("error") or {}
        code = str(error.get("code") or "")
        message = str(error.get("message") or message)
    except json.JSONDecodeError:
        pass
    return CasApiError(message=message, status=exc.code, code=code)
