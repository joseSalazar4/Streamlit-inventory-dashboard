from __future__ import annotations

import re
from typing import Dict

import streamlit as st

from auth.email_codes import (
    MAX_EMAIL_CODE_ATTEMPTS,
    create_email_challenge,
    get_attempts_remaining,
    validate_email_code,
)
from auth.resend_email import (
    get_last_email_error,
    send_verification_code,
)


def password_requirements(password: str) -> Dict[str, bool]:
    return {
        "At least 8 characters": len(password) >= 8,
        "At least one number": bool(re.search(r"\d", password)),
        "At least one special character": bool(re.search(r"[^A-Za-z0-9]", password)),
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


def _password_is_valid(password: str) -> bool:
    return all(password_requirements(password).values())


def _start_signup(username: str, full_name: str, email: str, password: str) -> bool:
    code, challenge = create_email_challenge()
    if not send_verification_code(email, code):
        return False

    st.session_state.pending_signup = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "password": password,
    }
    st.session_state.email_challenge = challenge
    st.session_state.auth_step = "verify"
    return True


def _complete_signup() -> None:
    pending = st.session_state.pending_signup
    # SQL TODO: INSERT INTO users (username, full_name, email_hash, password_hash, email_verified) VALUES (..., ..., ..., ..., 1).
    st.session_state.authenticated_user = {
        "username": pending["username"],
        "full_name": pending["full_name"],
        "email": pending["email"],
    }
    for key in ("signup_username", "signup_full_name", "signup_email", "signup_password", "email_code"):
        st.session_state.pop(key, None)
    st.session_state.pending_signup = None
    st.session_state.email_challenge = None
    st.session_state.auth_step = "signup"
    st.session_state.page = "Dashboard"
    st.rerun()


def _render_signup_form() -> None:
    st.markdown("### Create your account")
    username = st.text_input("Username", key="signup_username")
    full_name = st.text_input("Full name", key="signup_full_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    st.caption("Password requirements: 8+ characters, number, special character.")
    password_ok = _password_is_valid(password)

    if st.button("Send verification code", type="primary", use_container_width=True):
        if not username or not full_name or not email or not password:
            st.error("Complete all fields.")
            return
        if not password_ok:
            st.error("Complete the password requirements.")
            return
        if not _start_signup(username, full_name, email, password):
            st.error("Could not send the verification email. Check the Resend email setup.")
            if get_last_email_error():
                st.caption(get_last_email_error())
            return
        st.rerun()


def _render_code_step() -> None:
    pending = st.session_state.get("pending_signup") or {}
    challenge = st.session_state.get("email_challenge")
    attempts_remaining = get_attempts_remaining(challenge)
    st.markdown("### Verify your email")
    st.caption(f"Enter the 6-digit code for {pending.get('email', 'your email')}.")
    st.caption(f"Attempts remaining: {attempts_remaining} of {MAX_EMAIL_CODE_ATTEMPTS}")
    if attempts_remaining <= 0:
        st.warning("Too many incorrect attempts. Send a new code to try again.")
    code = st.text_input("Verification code", max_chars=6, key="email_code")

    left, right = st.columns(2)
    with left:
        if st.button("Verify code", type="primary", use_container_width=True, disabled=attempts_remaining <= 0):
            ok, message = validate_email_code(code, st.session_state.get("email_challenge"))
            if ok:
                st.success(message)
                _complete_signup()
            else:
                st.error(message)
    with right:
        if st.button("Send new code", use_container_width=True):
            pending = st.session_state.get("pending_signup")
            if pending:
                code, challenge = create_email_challenge()
                st.session_state.email_challenge = challenge
                if not send_verification_code(pending["email"], code):
                    st.error("Could not send the verification email. Check the Resend email setup.")
                    if get_last_email_error():
                        st.caption(get_last_email_error())
                    return
                st.rerun()


def _render_sign_in() -> None:
    st.markdown("### Sign in")
    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")

    if st.button("Sign in", type="primary", use_container_width=True):
        if not username or not password:
            st.error("Enter your username and password.")
            return
        if username.strip().lower() == "admin" and password.strip().lower() == "admin":
            st.session_state.authenticated_user = {
                "username": "admin",
                "full_name": "Admin",
                "email": "",
            }
            st.session_state.page = "Dashboard"
            st.rerun()
        # TODO: Authenticate user against database.
        st.info("Sign in will be enabled when the database connection is added.")


def auth_page() -> None:
    with st.container(key="auth_shell"):
        with st.container(border=True, key="auth_card"):
            _auth_header()
            st.caption("Sign in or create an account to continue.")
            if st.session_state.get("auth_step") == "verify":
                _render_code_step()
                return

            mode = st.radio(
                "Authentication mode",
                ["Sign In", "Sign Up"],
                horizontal=True,
                label_visibility="collapsed",
                key="auth_mode",
            )
            if mode == "Sign In":
                _render_sign_in()
            else:
                _render_signup_form()
