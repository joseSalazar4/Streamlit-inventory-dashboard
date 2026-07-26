from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import string
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from threading import Lock
from typing import Dict
from urllib import request
from urllib.error import HTTPError, URLError

from cas_api.clients.dataverse import DataverseClient
from cas_api.config import ApiConfig


PASSWORD_ITERATIONS = 310_000
TEMPORARY_PASSWORD_TTL_SECONDS = 20 * 60
PASSWORD_CHANGE_TOKEN_TTL_SECONDS = 10 * 60
RESET_REQUEST_COOLDOWN_SECONDS = 60
PASSWORD_ALPHABET = string.ascii_letters + string.digits
_RESET_REQUESTS: Dict[str, float] = {}
_RESET_REQUESTS_LOCK = Lock()


@dataclass(frozen=True)
class AuthFlowError(RuntimeError):
    status: int
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class PasswordCheck:
    valid: bool
    temporary: bool = False
    expired: bool = False


def normalize_email(email: str) -> str:
    return email.strip().lower()


def generate_temporary_password(length: int = 12) -> str:
    if length < 10:
        raise ValueError("Temporary passwords must contain at least 10 characters.")
    characters = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
    ]
    characters.extend(secrets.choice(PASSWORD_ALPHABET) for _ in range(length - 3))
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def validate_new_password(password: str) -> str | None:
    if len(password) < 10:
        return "Use at least 10 characters."
    if len(password) > 128:
        return "Use no more than 128 characters."
    if not any(character.islower() for character in password):
        return "Include at least one lowercase letter."
    if not any(character.isupper() for character in password):
        return "Include at least one uppercase letter."
    if not any(character.isdigit() for character in password):
        return "Include at least one number."
    return None


def hash_password(
    password: str,
    *,
    temporary_expires_at: int | None = None,
    salt: bytes | None = None,
) -> str:
    resolved_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        resolved_salt,
        PASSWORD_ITERATIONS,
    )
    encoded = "$".join(
        [
            "pbkdf2_sha256",
            str(PASSWORD_ITERATIONS),
            _b64_encode(resolved_salt),
            _b64_encode(digest),
        ]
    )
    if temporary_expires_at is not None:
        return f"temporary${int(temporary_expires_at)}${encoded}"
    return encoded


def verify_password(
    password: str,
    encoded_password: str,
    *,
    now: int | None = None,
) -> PasswordCheck:
    temporary = False
    expires_at = 0
    encoded = encoded_password
    if encoded.startswith("temporary$"):
        temporary = True
        try:
            _, raw_expiry, encoded = encoded.split("$", 2)
            expires_at = int(raw_expiry)
        except (TypeError, ValueError):
            return PasswordCheck(False)

    try:
        algorithm, raw_iterations, raw_salt, raw_digest = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return PasswordCheck(False, temporary=temporary)
        iterations = int(raw_iterations)
        if not 100_000 <= iterations <= 1_000_000:
            return PasswordCheck(False, temporary=temporary)
        salt = _b64_decode(raw_salt)
        expected = _b64_decode(raw_digest)
    except (TypeError, ValueError):
        return PasswordCheck(False, temporary=temporary)

    current_time = int(time.time()) if now is None else int(now)
    if temporary and current_time > expires_at:
        return PasswordCheck(False, temporary=True, expired=True)

    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return PasswordCheck(
        hmac.compare_digest(actual, expected),
        temporary=temporary,
    )


class PortalAuthStore:
    def __init__(self, config: ApiConfig):
        self.client = DataverseClient(config)

    def get_user_by_email(self, email: str) -> Dict[str, object] | None:
        escaped_email = normalize_email(email).replace("'", "''")
        rows = self.client._list_rows(
            "opti_portal_users",
            [
                "opti_portal_usersid",
                "opti_id_portal_user",
                "opti_email",
                "opti_password_hash",
                "opti_tipo_usuario",
                "_opti_id_estudiante_value",
                "opti_email_verified",
                "opti_activo",
            ],
            filters=[f"opti_email eq '{escaped_email}'"],
            top=1,
        )
        return rows[0] if rows else None

    def student_for_user(self, user: Dict[str, object]) -> Dict[str, object] | None:
        student_row_id = str(user.get("_opti_id_estudiante_value") or "").strip()
        if not student_row_id:
            return None
        rows = self.client._list_rows(
            "cr65d_estudiantes",
            self.client._student_select_fields(),
            filters=[f"cr65d_estudiantesid eq {student_row_id}"],
            top=1,
        )
        return self.client._map_student(rows[0]) if rows else None

    def student_by_email(self, email: str) -> Dict[str, object] | None:
        escaped_email = normalize_email(email).replace("'", "''")
        rows = self.client._list_rows(
            "cr65d_estudiantes",
            self.client._student_select_fields(),
            filters=[f"cr65d_email eq '{escaped_email}'"],
            top=1,
        )
        return self.client._map_student(rows[0]) if rows else None

    def create_student_user(
        self,
        email: str,
        student: Dict[str, object],
        password_hash: str,
    ) -> Dict[str, object]:
        student_row_id = str(student.get("dataverse_id") or "").strip()
        if not student_row_id:
            raise RuntimeError("Student is missing its Dataverse row ID.")
        student_type = self.client._choice_values(
            "opti_portal_users",
            "opti_tipo_usuario",
        ).get("student")
        if student_type is None:
            raise RuntimeError("Portal user type 'student' is not configured.")

        payload = {
            "opti_id_portal_user": f"portal_{uuid.uuid4().hex}",
            "opti_email": normalize_email(email),
            "opti_password_hash": password_hash,
            "opti_tipo_usuario": student_type,
            "opti_email_verified": True,
            "opti_activo": True,
            "opti_id_estudiante@odata.bind": (
                f"/{self.client._entity_set('cr65d_estudiantes')}({student_row_id})"
            ),
        }
        self.client._create_row("opti_portal_users", payload)
        created = self.get_user_by_email(email)
        if not created:
            raise RuntimeError("Portal user was created but could not be read back.")
        return created

    def user_type(self, user: Dict[str, object]) -> str:
        raw_value = user.get("opti_tipo_usuario")
        if raw_value is None:
            return ""
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            return str(raw_value).strip().lower()
        return self.client._choice_labels_by_value(
            "opti_portal_users",
            "opti_tipo_usuario",
        ).get(value, "")

    def set_password_hash(self, user: Dict[str, object], password_hash: str) -> None:
        row_id = str(user.get("opti_portal_usersid") or "").strip()
        if not row_id:
            raise RuntimeError("Portal user is missing its Dataverse row ID.")
        self.client._patch_row(
            "opti_portal_users",
            row_id,
            {"opti_password_hash": password_hash},
        )
        user["opti_password_hash"] = password_hash

    def record_login(self, user: Dict[str, object]) -> None:
        row_id = str(user.get("opti_portal_usersid") or "").strip()
        if not row_id:
            return
        logged_in_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.client._patch_row(
            "opti_portal_users",
            row_id,
            {"opti_ultimo_login": logged_in_at},
        )


class ResendPasswordMailer:
    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        portal_url: str | None = None,
    ):
        self.api_key = (api_key or os.getenv("RESEND_API_KEY", "")).strip()
        self.from_email = (
            from_email or os.getenv("RESEND_FROM_EMAIL", "")
        ).strip()
        self.portal_url = (
            portal_url or os.getenv("CAS_PORTAL_URL", "")
        ).strip()

    def is_configured(self) -> bool:
        return bool(
            self.api_key
            and self.from_email
            and self.portal_url
        )

    def send_temporary_password(
        self,
        to_email: str,
        temporary_password: str,
        recipient_name: str = "",
    ) -> None:
        if not self.is_configured():
            raise AuthFlowError(
                503,
                "password_email_not_configured",
                "Password reset email is not configured.",
            )

        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": "Your temporary CAS password",
            "html": _temporary_password_email_html(
                temporary_password,
                recipient_name,
                self.portal_url,
            ),
            "text": (
                f"Your temporary CAS password is {temporary_password}. "
                "It expires in 20 minutes. Sign in and create a new password at "
                f"{self.portal_url}"
            ),
        }
        email_request = request.Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": f"password-reset-{uuid.uuid4().hex}",
            },
            method="POST",
        )
        try:
            with request.urlopen(email_request, timeout=20) as response:
                if response.status not in {200, 201}:
                    raise AuthFlowError(
                        503,
                        "password_email_failed",
                        "Password reset email could not be sent.",
                    )
        except AuthFlowError:
            raise
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError) as exc:
            raise AuthFlowError(
                503,
                "password_email_failed",
                "Password reset email could not be sent.",
            ) from exc


class PasswordResetService:
    def __init__(
        self,
        store: PortalAuthStore,
        mailer: ResendPasswordMailer,
        *,
        token_secret: str,
    ):
        self.store = store
        self.mailer = mailer
        self.token_secret = token_secret.strip()

    @classmethod
    def from_env(cls) -> "PasswordResetService":
        return cls(
            PortalAuthStore(ApiConfig.from_env()),
            ResendPasswordMailer(),
            token_secret=os.getenv("CAS_API_PASSWORD_RESET_SECRET", ""),
        )

    def request_password_reset(self, email: str) -> Dict[str, object]:
        normalized_email = normalize_email(email)
        if not normalized_email or "@" not in normalized_email:
            raise AuthFlowError(400, "invalid_email", "Enter a valid email address.")
        self._require_reset_configuration()
        if not _claim_reset_request(normalized_email):
            return {"message": "password_reset_requested"}

        temporary_password = generate_temporary_password()
        expires_at = int(time.time()) + TEMPORARY_PASSWORD_TTL_SECONDS
        temporary_hash = hash_password(
            temporary_password,
            temporary_expires_at=expires_at,
        )
        user = self.store.get_user_by_email(normalized_email)
        created_user = False
        if not user:
            student = self.store.student_by_email(normalized_email)
            if not student:
                return {"message": "password_reset_requested"}
            user = self.store.create_student_user(
                normalized_email,
                student,
                temporary_hash,
            )
            created_user = True
        elif user.get("opti_activo") is False:
            return {"message": "password_reset_requested"}
        else:
            student = self.store.student_for_user(user) or {}

        previous_hash = str(user.get("opti_password_hash") or "")
        if not created_user:
            self.store.set_password_hash(user, temporary_hash)
        try:
            self.mailer.send_temporary_password(
                normalized_email,
                temporary_password,
                str(student.get("full_name") or ""),
            )
        except Exception:
            safe_hash = (
                hash_password(generate_temporary_password())
                if created_user
                else previous_hash
            )
            self.store.set_password_hash(user, safe_hash)
            _release_reset_request(normalized_email)
            raise
        return {"message": "password_reset_requested"}

    def authenticate(self, email: str, password: str) -> Dict[str, object]:
        normalized_email = normalize_email(email)
        user = self.store.get_user_by_email(normalized_email)
        if not user or user.get("opti_activo") is False:
            raise AuthFlowError(401, "invalid_credentials", "Invalid email or password.")
        if user.get("opti_email_verified") is False:
            raise AuthFlowError(403, "email_not_verified", "Verify your email before signing in.")

        encoded_password = str(user.get("opti_password_hash") or "")
        password_check = verify_password(password, encoded_password)
        if not password_check.valid:
            code = "temporary_password_expired" if password_check.expired else "invalid_credentials"
            raise AuthFlowError(401, code, "Invalid email or password.")
        if self.store.user_type(user) != "student":
            raise AuthFlowError(403, "students_only", "This portal is available to students only.")

        student = self.store.student_for_user(user)
        if not student or not student.get("student_id"):
            raise AuthFlowError(
                403,
                "student_not_linked",
                "Your account is not linked to a student profile.",
            )

        response: Dict[str, object] = {
            "user": {
                "user_id": user.get("opti_id_portal_user"),
                "email": normalized_email,
                "user_type": "student",
                "student_id": student.get("student_id"),
                "password_change_required": password_check.temporary,
            }
        }
        if password_check.temporary:
            self._require_token_secret()
            response["password_change_token"] = self._create_change_token(
                normalized_email,
                encoded_password,
            )
        else:
            self.store.record_login(user)
        return response

    def change_password(
        self,
        email: str,
        change_token: str,
        new_password: str,
    ) -> Dict[str, object]:
        normalized_email = normalize_email(email)
        password_error = validate_new_password(new_password)
        if password_error:
            raise AuthFlowError(400, "weak_password", password_error)

        user = self.store.get_user_by_email(normalized_email)
        if not user or user.get("opti_activo") is False:
            raise AuthFlowError(401, "invalid_change_token", "Request a new password reset.")
        current_hash = str(user.get("opti_password_hash") or "")
        self._verify_change_token(change_token, normalized_email, current_hash)
        current_check = verify_password("", current_hash)
        if not current_check.temporary or current_check.expired:
            raise AuthFlowError(401, "invalid_change_token", "Request a new password reset.")
        if verify_password(new_password, current_hash).valid:
            raise AuthFlowError(
                400,
                "password_unchanged",
                "Choose a password different from the temporary password.",
            )

        self.store.set_password_hash(user, hash_password(new_password))
        self.store.record_login(user)
        return {"message": "password_changed"}

    def _require_reset_configuration(self) -> None:
        self._require_token_secret()
        if not self.mailer.is_configured():
            raise AuthFlowError(
                503,
                "password_email_not_configured",
                "Password reset email is not configured.",
            )

    def _require_token_secret(self) -> None:
        if len(self.token_secret) < 24:
            raise AuthFlowError(
                503,
                "password_reset_not_configured",
                "Password reset is not configured.",
            )

    def _create_change_token(self, email: str, password_hash: str) -> str:
        payload = {
            "email": email,
            "exp": int(time.time()) + PASSWORD_CHANGE_TOKEN_TTL_SECONDS,
            "password": hashlib.sha256(password_hash.encode("utf-8")).hexdigest(),
        }
        body = _b64_encode(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signature = hmac.new(
            self.token_secret.encode("utf-8"),
            body.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{body}.{_b64_encode(signature)}"

    def _verify_change_token(
        self,
        token: str,
        email: str,
        password_hash: str,
    ) -> None:
        try:
            body, raw_signature = token.split(".", 1)
            signature = _b64_decode(raw_signature)
            expected = hmac.new(
                self.token_secret.encode("utf-8"),
                body.encode("ascii"),
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError("signature")
            payload = json.loads(_b64_decode(body))
            expected_password = hashlib.sha256(password_hash.encode("utf-8")).hexdigest()
            if payload.get("email") != email:
                raise ValueError("email")
            if int(payload.get("exp") or 0) < int(time.time()):
                raise ValueError("expired")
            if not hmac.compare_digest(
                str(payload.get("password") or ""),
                expected_password,
            ):
                raise ValueError("password")
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AuthFlowError(
                401,
                "invalid_change_token",
                "Request a new password reset.",
            ) from exc


def _claim_reset_request(email: str) -> bool:
    now = time.monotonic()
    with _RESET_REQUESTS_LOCK:
        previous = _RESET_REQUESTS.get(email, 0.0)
        if now - previous < RESET_REQUEST_COOLDOWN_SECONDS:
            return False
        _RESET_REQUESTS[email] = now
    return True


def _release_reset_request(email: str) -> None:
    with _RESET_REQUESTS_LOCK:
        _RESET_REQUESTS.pop(email, None)


def _temporary_password_email_html(
    temporary_password: str,
    recipient_name: str,
    portal_url: str,
) -> str:
    safe_password = escape(temporary_password)
    safe_portal_url = escape(portal_url, quote=True)
    greeting = f"Hello {escape(recipient_name.strip())}," if recipient_name.strip() else "Hello,"
    return f"""
    <div style="margin:0;padding:0;background:#f7f3ea;">
      <div style="max-width:560px;margin:0 auto;padding:28px 16px;font-family:Arial,Helvetica,sans-serif;color:#103b25;">
        <div style="background:#fffdf8;border:1px solid #d7e2d2;border-radius:14px;padding:24px;">
          <div style="font-size:18px;font-weight:800;letter-spacing:.08em;color:#103b25;">CAS</div>
          <div style="font-size:11px;letter-spacing:.16em;color:#557463;margin-bottom:22px;">DOCUMENT PORTAL</div>
          <h1 style="margin:0 0 10px;font-size:24px;line-height:1.25;">Reset your password</h1>
          <p style="font-size:15px;line-height:1.6;color:#375a48;">
            {greeting} use the temporary password below to sign in.
          </p>
          <div style="background:#e4f0e3;border:1px solid #b9d2ba;border-radius:10px;padding:14px 18px;text-align:center;margin:20px 0;">
            <div style="font-size:12px;font-weight:800;color:#1b5936;letter-spacing:.1em;text-transform:uppercase;margin-bottom:7px;">Temporary password</div>
            <div style="font-family:Consolas,Monaco,monospace;font-size:24px;font-weight:800;letter-spacing:2px;color:#103b25;">{safe_password}</div>
          </div>
          <p style="font-size:14px;line-height:1.55;color:#557463;">
            Copy this password and use it within 20 minutes. You will be asked to create a new password immediately after signing in.
          </p>
          <div style="text-align:center;margin-top:22px;">
            <a href="{safe_portal_url}" style="display:inline-block;background:#1b5936;color:#ffffff;text-decoration:none;font-weight:800;border-radius:10px;padding:12px 18px;">Open CAS portal</a>
          </div>
        </div>
        <p style="margin:16px 0 0;text-align:center;font-size:12px;color:#6b7f72;">
          If you did not request this reset, contact CAS support.
        </p>
      </div>
    </div>
    """


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + ("=" * (-len(value) % 4)))
