from __future__ import annotations

import logging
import os
from typing import Any, Dict

import streamlit as st

from api.cas_api import (
    CasApiError,
    authenticate_student,
    change_password,
    get_admission_progress,
    request_password_reset,
)
from auth.session_cookie import start_auth_session


TEST_USERNAME = "admin"
TEST_PASSWORD = "admin"
LOGGER = logging.getLogger(__name__)
SAFE_ACCOUNT_ERRORS = {
    "This portal is available to students only.",
    "Your account is not linked to a student profile. Contact support.",
    "Your account information could not be verified. Contact support.",
}


def _auth_header() -> None:
    st.markdown(
        """
        <div class="auth-brand">
            <div class="auth-logo">CAS</div>
            <div>
                <div class="auth-title">Document Portal</div>
                <div class="auth-subtitle">Secure access</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _test_student() -> Dict[str, Any]:
    student_id = os.environ.get("CAS_TEST_STUDENT_ID", "").strip()
    return {
        "id": student_id,
        "student_id": student_id,
        "username": TEST_USERNAME,
        "email": "admin@local.test",
        "full_name": os.environ.get("CAS_TEST_STUDENT_NAME", "Test Student").strip() or "Test Student",
        "user_type": "student",
        "is_test_user": True,
    }


def _student_from_login(email: str, password: str) -> tuple[Dict[str, Any], Dict[str, Any] | None]:
    test_student_id = os.environ.get("CAS_TEST_STUDENT_ID", "").strip()
    if (
        test_student_id
        and email.strip().lower() == TEST_USERNAME
        and password == TEST_PASSWORD
    ):
        user = _test_student()
        try:
            progress = get_admission_progress(user["student_id"])
        except CasApiError:
            progress = None
        return user, progress

    payload = authenticate_student(email, password)
    api_user = payload.get("user") or {}
    if str(api_user.get("user_type") or "").lower() != "student":
        raise CasApiError("This portal is available to students only.")
    student_id = str(api_user.get("student_id") or "").strip()
    if not student_id:
        raise CasApiError("Your account is not linked to a student profile. Contact support.")

    progress = get_admission_progress(student_id)
    student = progress.get("student") or {}
    matched_email = str(student.get("email") or api_user.get("email") or "").strip().lower()
    if matched_email != email.strip().lower():
        raise CasApiError("Your account information could not be verified. Contact support.")
    user = {
        "id": student_id,
        "student_id": student_id,
        "username": matched_email,
        "email": matched_email,
        "full_name": str(student.get("full_name") or matched_email),
        "user_type": "student",
        "is_test_user": False,
        "password_change_required": bool(api_user.get("password_change_required")),
        "password_change_token": str(payload.get("password_change_token") or ""),
    }
    return user, progress


def _render_student_sign_in() -> None:
    with st.form("student_sign_in", enter_to_submit=True, border=False):
        email = st.text_input("Email or username", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")
        submitted = st.form_submit_button(
            "Sign in",
            type="primary",
            icon=":material/login:",
            width="stretch",
        )

    if submitted:
        if not email or not password:
            st.error("Enter your email and password.")
            return
        try:
            with st.spinner("Signing in..."):
                user, progress = _student_from_login(email, password)
        except CasApiError as exc:
            LOGGER.warning("Student sign-in failed: %s", exc)
            if exc.code == "temporary_password_expired":
                st.error("Your temporary password expired. Request a new password reset.")
            elif exc.status in {401, 403}:
                st.error("Invalid email or password.")
            elif str(exc) in SAFE_ACCOUNT_ERRORS:
                st.error(str(exc))
            else:
                st.error("We couldn't sign you in right now. Please try again.")
            return

        password_change_required = bool(user.pop("password_change_required", False))
        password_change_token = str(user.pop("password_change_token", ""))
        if password_change_required:
            if not password_change_token:
                st.error("Password reset could not be completed. Request a new reset.")
                return
            st.session_state.pending_auth_user = user
            st.session_state.pending_auth_progress = progress
            st.session_state.pending_auth_email = str(user.get("email") or email).strip().lower()
            st.session_state.password_change_token = password_change_token
            st.session_state.auth_view = "change_password"
            st.rerun()

        start_auth_session(user)
        st.session_state.admission_progress = progress
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button(
        "Forgot password?",
        key="forgot_password",
        type="tertiary",
        width="stretch",
    ):
        st.session_state.auth_view = "forgot_password"
        st.rerun()


def _render_forgot_password() -> None:
    with st.form("forgot_password_form", enter_to_submit=True, border=False):
        email = st.text_input("Student email", key="reset_email")
        submitted = st.form_submit_button(
            "Send password reset",
            type="primary",
            icon=":material/mail:",
            width="stretch",
        )

    if submitted:
        if not email:
            st.error("Enter your student email.")
        else:
            try:
                with st.spinner("Sending password reset..."):
                    request_password_reset(email)
                st.session_state.auth_notice = (
                    "If an account exists for that email, a temporary password has been sent."
                )
                st.session_state.auth_view = "sign_in"
                st.rerun()
            except CasApiError as exc:
                LOGGER.warning("Password reset request failed: %s", exc)
                st.error("Password reset is unavailable right now. Please try again later.")

    if st.button(
        "Back to sign in",
        key="reset_back_to_signin",
        icon=":material/arrow_back:",
        type="tertiary",
        width="stretch",
    ):
        st.session_state.auth_view = "sign_in"
        st.rerun()


def _clear_pending_password_change() -> None:
    st.session_state.pending_auth_user = None
    st.session_state.pending_auth_progress = None
    st.session_state.pending_auth_email = ""
    st.session_state.password_change_token = ""


def _render_change_password() -> None:
    pending_user = st.session_state.get("pending_auth_user") or {}
    email = str(st.session_state.get("pending_auth_email") or "")
    change_token = str(st.session_state.get("password_change_token") or "")
    if not pending_user or not email or not change_token:
        st.error("This password reset is no longer available. Request a new one.")
        if st.button(
            "Back to sign in",
            key="change_password_back_to_signin",
            icon=":material/arrow_back:",
            type="tertiary",
            width="stretch",
        ):
            _clear_pending_password_change()
            st.session_state.auth_view = "sign_in"
            st.rerun()
        return

    with st.form("change_password_form", enter_to_submit=True, border=False):
        new_password = st.text_input(
            "New password",
            type="password",
            key="new_password",
        )
        confirm_password = st.text_input(
            "Confirm new password",
            type="password",
            key="confirm_new_password",
        )
        st.caption("Use at least 10 characters with uppercase, lowercase, and a number.")
        submitted = st.form_submit_button(
            "Update password and sign in",
            type="primary",
            icon=":material/lock_reset:",
            width="stretch",
        )

    if submitted:
        if not new_password or not confirm_password:
            st.error("Enter and confirm your new password.")
            return
        if new_password != confirm_password:
            st.error("The passwords do not match.")
            return
        try:
            with st.spinner("Updating password..."):
                change_password(email, change_token, new_password)
        except CasApiError as exc:
            LOGGER.warning("Password change failed: %s", exc)
            if exc.code in {"weak_password", "password_unchanged"}:
                st.error(str(exc))
            else:
                st.error("This password reset has expired. Request a new one.")
            return

        progress = st.session_state.get("pending_auth_progress")
        start_auth_session(dict(pending_user))
        st.session_state.admission_progress = progress
        _clear_pending_password_change()
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button(
        "Back to sign in",
        key="change_password_back_to_signin",
        icon=":material/arrow_back:",
        type="tertiary",
        width="stretch",
    ):
        _clear_pending_password_change()
        st.session_state.auth_view = "sign_in"
        st.rerun()


def auth_page() -> None:
    with st.container(key="auth_shell"):
        with st.container(border=True, key="auth_card"):
            _auth_header()
            auth_view = st.session_state.get("auth_view")
            captions = {
                "forgot_password": "Enter your email to receive a temporary password.",
                "change_password": "Create a new password to finish signing in.",
            }
            st.caption(captions.get(auth_view, "Sign in to continue."))
            notice = st.session_state.pop("auth_notice", "")
            if notice:
                st.success(notice)
            if auth_view == "forgot_password":
                _render_forgot_password()
            elif auth_view == "change_password":
                _render_change_password()
            else:
                _render_student_sign_in()
