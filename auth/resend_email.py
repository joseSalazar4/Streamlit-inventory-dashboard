from __future__ import annotations

import os
from typing import Any, Dict

import streamlit as st

try:
    import resend
except ImportError:  # pragma: no cover - exercised only when dependency is missing
    resend = None

LAST_EMAIL_ERROR_KEY = "resend_email_last_error"


def _resend_settings() -> Dict[str, Any]:
    try:
        return dict(st.secrets.get("resend", {}))
    except Exception:
        return {}


def _get_setting(settings: Dict[str, Any], key: str, env_key: str, default: str = "") -> str:
    return str(settings.get(key) or os.environ.get(env_key, default)).strip()


def _set_last_error(message: str) -> None:
    st.session_state[LAST_EMAIL_ERROR_KEY] = message


def get_last_email_error() -> str:
    return str(st.session_state.get(LAST_EMAIL_ERROR_KEY, ""))


def _verification_email_html(code: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.5;">
        <h2 style="margin: 0 0 12px;">Verify your email</h2>
        <p style="margin: 0 0 16px;">Use this code to finish creating your CAS account:</p>
        <div style="font-size: 32px; font-weight: 700; letter-spacing: 8px; margin: 20px 0;">
            {code}
        </div>
        <p style="margin: 0 0 8px;">This code expires in 15 minutes.</p>
        <p style="margin: 0; color: #6b7280; font-size: 13px;">
            If you did not request this code, you can ignore this email.
        </p>
    </div>
    """


def _send_resend_email(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    _set_last_error("")
    settings = _resend_settings()
    api_key = _get_setting(settings, "api_key", "RESEND_API_KEY")
    from_email = _get_setting(settings, "from_email", "RESEND_FROM_EMAIL", "CAS <onboarding@resend.dev>")

    if resend is None:
        _set_last_error("Missing resend package. Run: pip install resend")
        return False
    if not api_key:
        _set_last_error("Missing resend.api_key in Streamlit secrets or RESEND_API_KEY.")
        return False
    if not from_email:
        _set_last_error("Missing resend.from_email in Streamlit secrets or RESEND_FROM_EMAIL.")
        return False

    try:
        resend.api_key = api_key
        params: resend.Emails.SendParams = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        resend.Emails.send(params)
        return True
    except Exception as error:
        _set_last_error(f"Could not send Resend email: {error}")
        return False


def send_verification_code(to_email: str, code: str) -> bool:
    return _send_resend_email(
        to_email,
        "Your CAS verification code",
        _verification_email_html(code),
        f"Your CAS verification code is {code}. It expires in 15 minutes.",
    )
