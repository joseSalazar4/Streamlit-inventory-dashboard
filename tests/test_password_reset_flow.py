from __future__ import annotations

import sys
import json
import threading
import unittest
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib import request


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_API = ROOT / ".local" / "cas-document-platform" / "cas-api"
UPSTREAM_API_AVAILABLE = (UPSTREAM_API / "cas_api" / "server.py").is_file()

if UPSTREAM_API_AVAILABLE:
    sys.path.insert(0, str(UPSTREAM_API))
    from local_api.portal_auth import (
        AuthFlowError,
        PasswordResetService,
        hash_password,
        verify_password,
    )
    from local_api.student_upload_server import StudentUploadApiHandler


class FakeStore:
    def __init__(self, email: str, *, has_user: bool = True):
        user = {
            "opti_portal_usersid": "ROW-1",
            "opti_id_portal_user": "PORTAL-1",
            "opti_email": email,
            "opti_password_hash": hash_password("OriginalPass1"),
            "opti_email_verified": True,
            "opti_activo": True,
        }
        self.user = user if has_user else None
        self.student = {
            "student_id": "EST-1",
            "full_name": "Ana Student",
            "email": email,
        }
        self.login_count = 0

    def get_user_by_email(self, email: str):
        if not self.user:
            return None
        return self.user if email == self.user["opti_email"] else None

    def student_for_user(self, user):
        return self.student

    def student_by_email(self, email: str):
        return self.student if email == self.student["email"] else None

    def create_student_user(self, email: str, student, password_hash: str):
        self.user = {
            "opti_portal_usersid": "ROW-NEW",
            "opti_id_portal_user": "PORTAL-NEW",
            "opti_email": email,
            "opti_password_hash": password_hash,
            "opti_email_verified": True,
            "opti_activo": True,
        }
        return self.user

    def user_type(self, user):
        return "student"

    def set_password_hash(self, user, password_hash: str):
        user["opti_password_hash"] = password_hash

    def record_login(self, user):
        self.login_count += 1


class FakeMailer:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.sent = []

    def is_configured(self) -> bool:
        return True

    def send_temporary_password(
        self,
        to_email: str,
        temporary_password: str,
        recipient_name: str = "",
    ) -> None:
        if self.fail:
            raise AuthFlowError(503, "password_email_failed", "Email failed.")
        self.sent.append((to_email, temporary_password, recipient_name))


class FakeRouteService:
    def request_password_reset(self, email: str):
        return {"message": "password_reset_requested"}

    def authenticate(self, email: str, password: str):
        return {
            "user": {
                "email": email,
                "user_type": "student",
                "student_id": "EST-1",
                "password_change_required": True,
            },
            "password_change_token": "signed-token",
        }

    def change_password(self, email: str, change_token: str, new_password: str):
        return {"message": "password_changed"}


@unittest.skipUnless(UPSTREAM_API_AVAILABLE, "Local CAS API checkout is not available.")
class PasswordResetFlowTests(unittest.TestCase):
    def _email(self) -> str:
        return f"student-{uuid.uuid4().hex}@example.test"

    def test_reset_stores_only_a_temporary_hash_and_sends_password(self) -> None:
        email = self._email()
        store = FakeStore(email)
        mailer = FakeMailer()
        service = PasswordResetService(
            store,
            mailer,
            token_secret="a-very-long-test-secret-value",
        )

        response = service.request_password_reset(email.upper())

        self.assertEqual(response["message"], "password_reset_requested")
        self.assertEqual(len(mailer.sent), 1)
        sent_email, temporary_password, recipient_name = mailer.sent[0]
        self.assertEqual(sent_email, email)
        self.assertEqual(recipient_name, "Ana Student")
        self.assertNotIn(temporary_password, store.user["opti_password_hash"])
        password_check = verify_password(
            temporary_password,
            store.user["opti_password_hash"],
        )
        self.assertTrue(password_check.valid)
        self.assertTrue(password_check.temporary)

    def test_temporary_login_forces_one_password_change(self) -> None:
        email = self._email()
        store = FakeStore(email)
        mailer = FakeMailer()
        service = PasswordResetService(
            store,
            mailer,
            token_secret="a-very-long-test-secret-value",
        )
        service.request_password_reset(email)
        temporary_password = mailer.sent[0][1]

        login = service.authenticate(email, temporary_password)

        self.assertTrue(login["user"]["password_change_required"])
        self.assertTrue(login["password_change_token"])
        self.assertEqual(store.login_count, 0)

        service.change_password(
            email,
            str(login["password_change_token"]),
            "NewSecurePass2",
        )
        self.assertEqual(store.login_count, 1)
        self.assertFalse(
            verify_password(
                temporary_password,
                store.user["opti_password_hash"],
            ).valid
        )

        next_login = service.authenticate(email, "NewSecurePass2")
        self.assertFalse(next_login["user"]["password_change_required"])
        self.assertNotIn("password_change_token", next_login)

    def test_email_failure_restores_previous_password_hash(self) -> None:
        email = self._email()
        store = FakeStore(email)
        previous_hash = str(store.user["opti_password_hash"])
        service = PasswordResetService(
            store,
            FakeMailer(fail=True),
            token_secret="a-very-long-test-secret-value",
        )

        with self.assertRaises(AuthFlowError):
            service.request_password_reset(email)

        self.assertEqual(store.user["opti_password_hash"], previous_hash)
        self.assertTrue(verify_password("OriginalPass1", previous_hash).valid)

    def test_unknown_email_returns_the_same_generic_response(self) -> None:
        email = self._email()
        store = FakeStore("other@example.test")
        service = PasswordResetService(
            store,
            FakeMailer(),
            token_secret="a-very-long-test-secret-value",
        )

        response = service.request_password_reset(email)

        self.assertEqual(response["message"], "password_reset_requested")

    def test_existing_student_is_provisioned_on_first_reset(self) -> None:
        email = self._email()
        store = FakeStore(email, has_user=False)
        mailer = FakeMailer()
        service = PasswordResetService(
            store,
            mailer,
            token_secret="a-very-long-test-secret-value",
        )

        service.request_password_reset(email)

        self.assertIsNotNone(store.user)
        self.assertEqual(store.user["opti_email"], email)
        self.assertEqual(len(mailer.sent), 1)
        self.assertTrue(
            verify_password(
                mailer.sent[0][1],
                store.user["opti_password_hash"],
            ).valid
        )

    def test_password_policy_rejects_weak_replacement(self) -> None:
        email = self._email()
        store = FakeStore(email)
        mailer = FakeMailer()
        service = PasswordResetService(
            store,
            mailer,
            token_secret="a-very-long-test-secret-value",
        )
        service.request_password_reset(email)
        login = service.authenticate(email, mailer.sent[0][1])

        with self.assertRaises(AuthFlowError) as raised:
            service.change_password(
                email,
                str(login["password_change_token"]),
                "short",
            )

        self.assertEqual(raised.exception.code, "weak_password")

    def test_all_three_password_routes_are_registered(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), StudentUploadApiHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        payloads = {
            "/auth/forgot-password": {"email": "ana@example.test"},
            "/auth/login": {
                "email": "ana@example.test",
                "password": "Temporary1",
            },
            "/auth/change-password": {
                "email": "ana@example.test",
                "change_token": "signed-token",
                "new_password": "NewSecurePass2",
            },
        }
        try:
            with patch(
                "local_api.student_upload_server.PasswordResetService.from_env",
                return_value=FakeRouteService(),
            ):
                responses = {}
                for path, payload in payloads.items():
                    api_request = request.Request(
                        f"http://127.0.0.1:{server.server_port}{path}",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with request.urlopen(api_request, timeout=5) as response:
                        responses[path] = (
                            response.status,
                            json.loads(response.read().decode("utf-8")),
                        )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(responses["/auth/forgot-password"][0], 202)
        self.assertEqual(responses["/auth/login"][0], 200)
        self.assertTrue(
            responses["/auth/login"][1]["user"]["password_change_required"]
        )
        self.assertEqual(
            responses["/auth/change-password"][1]["message"],
            "password_changed",
        )


if __name__ == "__main__":
    unittest.main()
