from __future__ import annotations

import os
from html import escape
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


def _verification_email_html(
    code: str,
    recipient_name: str = "",
    title: str = "Verify your email",
    intro: str = "use this code to finish creating your secure CAS account.",
    preheader: str = "Use this code to finish creating your CAS Document Portal account.",
    code_label: str = "Verification code",
) -> str:
    safe_code = escape(code)
    greeting = f"Hi {escape(recipient_name.strip())}," if recipient_name.strip() else "Hello,"
    safe_title = escape(title)
    safe_intro = escape(intro)
    safe_preheader = escape(preheader)
    safe_code_label = escape(code_label)
    return f"""
    <div style="margin:0; padding:0; background:#f7f3ea;">
      <div style="display:none; max-height:0; overflow:hidden; opacity:0;">
        {safe_preheader}
      </div>
      <div style="max-width:560px; margin:0 auto; padding:28px 16px; font-family:Arial, Helvetica, sans-serif; color:#103b25;">
        <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%; margin-bottom:18px;">
          <tr>
            <td style="width:56px; vertical-align:middle;">
              <div style="width:44px; height:44px; border-radius:12px; background:#1b5936; color:#ffffff; font-size:12px; font-weight:800; line-height:44px; text-align:center;">
                CAS
              </div>
            </td>
            <td style="vertical-align:middle;">
              <div style="font-size:18px; font-weight:800; letter-spacing:.08em; color:#103b25;">CAS</div>
              <div style="font-size:11px; letter-spacing:.16em; color:#557463;">DOCUMENT PORTAL</div>
            </td>
          </tr>
        </table>

        <div style="background:#fffdf8; border:1px solid #d7e2d2; border-radius:14px; padding:24px; box-shadow:0 10px 24px rgba(57,57,57,.06);">
          <h1 style="margin:0 0 10px; font-size:24px; line-height:1.25; color:#103b25;">{safe_title}</h1>
          <p style="margin:0 0 18px; font-size:15px; line-height:1.6; color:#375a48;">
            {greeting} {safe_intro}
          </p>

          <div style="background:#e7f3e7; border:1px solid #b9d8b9; border-radius:12px; padding:18px 12px; text-align:center; margin:18px 0;">
            <div style="font-size:12px; font-weight:800; color:#1b5936; letter-spacing:.12em; text-transform:uppercase; margin-bottom:8px;">
              {safe_code_label}
            </div>
            <div style="font-size:34px; line-height:1; font-weight:800; letter-spacing:8px; color:#103b25;">
              {safe_code}
            </div>
          </div>

          <p style="margin:0; font-size:14px; line-height:1.55; color:#557463;">
            This code expires in 15 minutes. If you did not request this code, you can safely ignore this email.
          </p>
        </div>

        <p style="margin:16px 0 0; text-align:center; font-size:12px; line-height:1.5; color:#6b7f72;">
          CAS Document Portal
        </p>
      </div>
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


def send_verification_code(to_email: str, code: str, recipient_name: str = "") -> bool:
    return _send_resend_email(
        to_email,
        "Verify your CAS account",
        _verification_email_html(code, recipient_name),
        f"Your CAS verification code is {code}. It expires in 15 minutes.",
    )


def send_password_reset_code(to_email: str, code: str, recipient_name: str = "") -> bool:
    return _send_resend_email(
        to_email,
        "Reset your CAS password",
        _verification_email_html(
            code,
            recipient_name,
            title="Reset your password",
            intro="use this code to reset your CAS account password.",
            preheader="Use this code to reset your CAS Document Portal password.",
            code_label="Reset code",
        ),
        f"Your CAS password reset code is {code}. It expires in 15 minutes.",
    )
