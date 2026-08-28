import unittest

from auth.session_cookie import COOKIE_NAME


class StudentCookieScopeTests(unittest.TestCase):
    def test_student_cookie_has_portal_specific_name(self) -> None:
        self.assertEqual(COOKIE_NAME, "cas_student_auth")


if __name__ == "__main__":
    unittest.main()
