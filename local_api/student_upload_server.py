from __future__ import annotations

import cgi
import os
import re
import time
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from typing import Dict, Tuple
from urllib.parse import unquote, urlparse

from cas_api.clients.dataverse import DOCUMENT_STATUS_VALUE, DataverseClient
from cas_api.clients.sharepoint import SharePointClient
from cas_api.config import ApiConfig
from cas_api.http import HttpError
from cas_api.server import CasApiHandler

from local_api.portal_auth import AuthFlowError, PasswordResetService
from validators.file_content import MAX_FILE_SIZE_BYTES, safe_ext, validate_file


MAX_MULTIPART_OVERHEAD_BYTES = 1024 * 1024


class StudentUploadDataverseClient(DataverseClient):
    def prepare_student_file_upload(
        self,
        student_id: str,
        document_type_id: str,
        file_name: str,
    ) -> int:
        student, document_type, existing = self._student_upload_context(
            student_id,
            document_type_id,
        )
        del student

        allowed = {
            str(extension).lower().lstrip(".")
            for extension in document_type.get("allowed_file_types", [])
            if extension
        }
        extension = safe_ext(file_name)
        if allowed and extension not in allowed:
            raise ValueError(
                f"Document type {document_type_id} does not allow .{extension} files."
            )
        return _next_sharepoint_version(existing)

    def upsert_student_file_reference(
        self,
        student_id: str,
        document_type_id: str,
        sharepoint_item_id: str,
        sharepoint_web_url: str,
        file_name: str,
    ) -> Dict[str, object]:
        student, document_type, existing = self._student_upload_context(
            student_id,
            document_type_id,
        )
        version = _next_sharepoint_version(existing)
        status = "pending_review" if document_type.get("requires_review") else "approved"
        uploaded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        payload: Dict[str, object] = {
            "cr65d_estadodocumento": DOCUMENT_STATUS_VALUE[status],
            "cr65d_fechaentrega": uploaded_at,
            "opti_sharepoint_item_id": sharepoint_item_id,
            "opti_sharepoint_web_url": sharepoint_web_url,
            "opti_nombre_archivo": file_name,
            "opti_revisado_fecha": None,
            "opti_comentario_rechazo": None,
        }

        if existing and existing.get("dataverse_id"):
            document_id = str(
                existing.get("document_id")
                or f"doc_{student_id}_{document_type_id}"
            )
            self._patch_row(
                "cr65d_documentos_estudiantes",
                str(existing["dataverse_id"]),
                payload,
            )
        else:
            document_id = f"doc_{student_id}_{document_type_id}"
            payload["cr65d_id_documento"] = document_id
            self._set_student_reference(payload, student)
            self._set_document_type_reference(payload, document_type)
            self._create_row("cr65d_documentos_estudiantes", payload)

        return {
            "document_id": document_id,
            "student_id": student_id,
            "document_type_id": document_type_id,
            "status": status,
            "version": version,
            "file_name": file_name,
            "uploaded_at": uploaded_at,
            "student_file_available": True,
            "sharepoint_item_id": sharepoint_item_id,
            "sharepoint_web_url": sharepoint_web_url,
        }

    def _student_upload_context(
        self,
        student_id: str,
        document_type_id: str,
    ) -> Tuple[Dict[str, object], Dict[str, object], Dict[str, object] | None]:
        student = self.get_student(student_id)
        if not student:
            raise ValueError(f"Student not found: {student_id}")

        document_types = {
            str(item["document_type_id"]): item
            for item in self.list_document_types()
        }
        document_type = document_types.get(document_type_id)
        if not document_type:
            raise ValueError(f"Document type not found: {document_type_id}")
        if not document_type.get("can_student_upload"):
            raise ValueError(
                f"Document type does not allow student upload: {document_type_id}"
            )

        existing_documents = self.list_student_documents(
            student_id,
            student=student,
            document_types=list(document_types.values()),
        )
        existing = next(
            (
                document
                for document in existing_documents
                if str(document.get("document_type_id")) == document_type_id
            ),
            None,
        )
        return student, document_type, existing


class StudentUploadApiHandler(CasApiHandler):
    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path in {
            "/auth/login",
            "/auth/forgot-password",
            "/auth/change-password",
        }:
            self._request_started_at = time.perf_counter()
            self._handle_student_auth(path)
            return
        if path == "/documents/upload" or (
            path.startswith("/students/")
            and "/documents/" in path
            and path.endswith("/student-file")
        ):
            self._request_started_at = time.perf_counter()
            self._handle_student_upload(path)
            return
        super().do_POST()

    def _handle_student_auth(self, path: str) -> None:
        try:
            status, body = self._student_auth_response(path)
            self._send_json(status, body)
        except AuthFlowError as exc:
            self._send_json(
                exc.status,
                {
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
            )
        except HttpError:
            self._send_json(
                503,
                {
                    "error": {
                        "code": "account_service_unavailable",
                        "message": "Account services are unavailable.",
                    }
                },
            )
        except Exception as exc:
            print(f"Password flow error: {exc}", flush=True)
            self._send_json(
                500,
                {
                    "error": {
                        "code": "internal_error",
                        "message": "The request could not be completed.",
                    }
                },
            )

    def _student_auth_response(self, path: str) -> Tuple[int, Dict[str, object]]:
        payload = self._read_json_body()
        service = PasswordResetService.from_env()
        email = str(payload.get("email") or "")
        if path == "/auth/forgot-password":
            return 202, service.request_password_reset(email)
        if path == "/auth/login":
            password = str(payload.get("password") or "")
            if not email or not password:
                raise AuthFlowError(
                    400,
                    "missing_credentials",
                    "Email and password are required.",
                )
            return 200, service.authenticate(email, password)

        change_token = str(payload.get("change_token") or "")
        new_password = str(payload.get("new_password") or "")
        if not email or not change_token or not new_password:
            raise AuthFlowError(
                400,
                "missing_password_change_fields",
                "Email, reset authorization, and new password are required.",
            )
        return 200, service.change_password(
            email,
            change_token,
            new_password,
        )

    def _handle_student_upload(self, path: str) -> None:
        try:
            status, body = self._student_upload_response(path)
            self._send_json(status, body)
        except HttpError as exc:
            self._send_json(
                502,
                {
                    "error": {
                        "code": "microsoft_service_error",
                        "message": exc.body or str(exc),
                    }
                },
            )
        except ValueError as exc:
            self._send_json(
                400,
                {
                    "error": {
                        "code": "bad_request",
                        "message": str(exc),
                    }
                },
            )
        except Exception as exc:
            self._send_json(
                500,
                {
                    "error": {
                        "code": "internal_error",
                        "message": str(exc),
                    }
                },
            )

    def _student_upload_response(self, path: str) -> Tuple[int, Dict[str, object]]:
        form, upload = self._read_student_upload()
        if path == "/documents/upload":
            student_id = str(form.getfirst("student_id", "")).strip()
            document_type_id = str(form.getfirst("document_type_id", "")).strip()
        else:
            student_id, document_type_id = _student_document_type_from_path(path)
        if not student_id:
            raise ValueError("student_id is required.")
        if not document_type_id:
            raise ValueError("document_type_id is required.")

        ok, message = validate_file(str(upload["file_name"]), upload["content"])
        if not ok:
            raise ValueError(message)

        config = ApiConfig.from_env()
        dataverse = StudentUploadDataverseClient(config)
        version = dataverse.prepare_student_file_upload(
            student_id,
            document_type_id,
            str(upload["file_name"]),
        )
        item = SharePointClient(config).upload_admission_file(
            student_id=student_id,
            document_type_id=document_type_id,
            version=version,
            file_name=str(upload["file_name"]),
            content=upload["content"],
            content_type=str(upload["content_type"]),
        )
        result = dataverse.upsert_student_file_reference(
            student_id=student_id,
            document_type_id=document_type_id,
            sharepoint_item_id=str(item.get("id") or ""),
            sharepoint_web_url=str(item.get("webUrl") or ""),
            file_name=str(item.get("name") or upload["file_name"]),
        )
        return 201, result

    def _read_student_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("Request content type must be multipart/form-data.")
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length header.") from exc
        if content_length <= 0:
            raise ValueError("Request body is empty.")
        if content_length > MAX_FILE_SIZE_BYTES + MAX_MULTIPART_OVERHEAD_BYTES:
            raise ValueError("The file is too large. The maximum size is 40 MB.")

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(content_length),
            },
        )
        field = form["file"] if "file" in form else None
        if field is None or isinstance(field, list) or not getattr(field, "filename", ""):
            raise ValueError("file is required.")
        content = field.file.read(MAX_FILE_SIZE_BYTES + 1)
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise ValueError("The file is too large. The maximum size is 40 MB.")
        return form, {
            "file_name": os.path.basename(field.filename),
            "content_type": field.type or "application/octet-stream",
            "content": content,
        }


def _student_document_type_from_path(path: str) -> Tuple[str, str]:
    parts = path.strip("/").split("/")
    if (
        len(parts) != 5
        or parts[0] != "students"
        or parts[2] != "documents"
        or parts[4] != "student-file"
    ):
        raise ValueError("Invalid student file upload path.")
    return unquote(parts[1]).strip(), unquote(parts[3]).strip()


def _next_sharepoint_version(document: Dict[str, object] | None) -> int:
    if not document:
        return 1
    web_url = str(document.get("sharepoint_web_url") or "")
    match = re.search(r"/(\d+)/[^/]+$", web_url)
    return int(match.group(1)) + 1 if match else 2


def run() -> None:
    host = os.getenv("CAS_API_HOST", "127.0.0.1")
    port = int(os.getenv("CAS_API_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), StudentUploadApiHandler)
    print(f"CAS API with student uploads listening on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
