import unittest

from api.cas_api import CasApiError
from app_pages.auth import _password_change_redirect


class PasswordChangeRedirectTests(unittest.TestCase):
    def test_temporary_password_redirects_to_change_password_context(self) -> None:
        user = {
            "email": "Student@Example.com",
            "student_id": "student-1",
            "password_change_required": True,
            "password_change_token": "signed-change-token",
        }
        progress = {"student": {"id": "student-1"}}

        authenticated_user, redirect = _password_change_redirect(user, progress, "ignored@example.com")

        self.assertNotIn("password_change_required", authenticated_user)
        self.assertNotIn("password_change_token", authenticated_user)
        self.assertEqual(redirect["email"], "student@example.com")
        self.assertEqual(redirect["token"], "signed-change-token")
        self.assertIs(redirect["progress"], progress)

    def test_regular_password_continues_to_dashboard(self) -> None:
        authenticated_user, redirect = _password_change_redirect(
            {"email": "student@example.com", "password_change_required": False},
            None,
            "student@example.com",
        )

        self.assertEqual(authenticated_user["email"], "student@example.com")
        self.assertIsNone(redirect)

    def test_missing_change_token_is_rejected(self) -> None:
        with self.assertRaises(CasApiError):
            _password_change_redirect(
                {"email": "student@example.com", "password_change_required": True},
                None,
                "student@example.com",
            )


if __name__ == "__main__":
    unittest.main()
