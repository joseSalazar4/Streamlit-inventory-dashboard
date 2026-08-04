from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

import streamlit as st
import streamlit.components.v1 as components


COOKIE_NAME = "cas_auth"
COOKIE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
PENDING_COOKIE_KEY = "_cas_cookie_update"
SKIP_COOKIE_RESTORE_KEY = "_cas_skip_cookie_restore"


def _auth_settings() -> Dict[str, Any]:
    try:
        return dict(st.secrets.get("auth", {}))
    except Exception:
        return {}


def _cookie_secret() -> bytes:
    settings = _auth_settings()
    secret = str(settings.get("cookie_secret") or os.environ.get("AUTH_COOKIE_SECRET") or "dev-cas-cookie-secret")
    return secret.encode("utf-8")


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + ("=" * (-len(value) % 4)))


def _clean_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(user.get("id") or user.get("student_id") or ""),
        "student_id": str(user.get("student_id") or user.get("id") or ""),
        "username": str(user.get("username") or user.get("email") or ""),
        "full_name": str(user.get("full_name", "")),
        "email": str(user.get("email", "")),
        "user_type": "student",
        "is_test_user": bool(user.get("is_test_user")),
    }


def _sign(value: str) -> str:
    digest = hmac.new(_cookie_secret(), value.encode("utf-8"), hashlib.sha256).digest()
    return _b64_encode(digest)


def _create_token(user: Dict[str, Any]) -> str:
    now = int(time.time())
    payload = {
        "exp": now + COOKIE_MAX_AGE_SECONDS,
        "iat": now,
        "user": _clean_user(user),
    }
    body = _b64_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    return f"{body}.{_sign(body)}"


def _read_token(token: str) -> Dict[str, Any] | None:
    try:
        body, signature = token.split(".", 1)
    except ValueError:
        return None

    if not hmac.compare_digest(signature, _sign(body)):
        return None

    try:
        payload = json.loads(_b64_decode(body))
    except Exception:
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    user = payload.get("user")
    if not isinstance(user, dict) or not user.get("email"):
        return None
    clean_user = _clean_user(user)

    return clean_user


def _queue_cookie(cookie: str) -> None:
    st.session_state[PENDING_COOKIE_KEY] = cookie


def _queue_set_cookie(token: str) -> None:
    _queue_cookie(f"{COOKIE_NAME}={token}; Max-Age={COOKIE_MAX_AGE_SECONDS}; Path=/; SameSite=Lax")


def _queue_clear_cookie() -> None:
    _queue_cookie(f"{COOKIE_NAME}=; Max-Age=0; Path=/; SameSite=Lax")


def render_cookie_update() -> None:
    cookie = st.session_state.pop(PENDING_COOKIE_KEY, "")
    if not cookie:
        return

    components.html(
        f"""
        <script>
        (function() {{
          const cookie = {json.dumps(cookie)};
          try {{
            window.parent.document.cookie = cookie;
          }} catch (error) {{
            document.cookie = cookie;
          }}
        }})();
        </script>
        """,
        height=0,
    )


def restore_auth_session() -> None:
    if st.session_state.pop(SKIP_COOKIE_RESTORE_KEY, False):
        return
    if st.session_state.get("authenticated_user"):
        return

    try:
        token = st.context.cookies.get(COOKIE_NAME, "")
    except Exception:
        token = ""

    if not token:
        return

    user = _read_token(token)
    if user:
        st.session_state.authenticated_user = user
    else:
        _queue_clear_cookie()


def start_auth_session(user: Dict[str, Any]) -> None:
    clean_user = _clean_user(user)
    st.session_state.authenticated_user = clean_user
    _queue_set_cookie(_create_token(clean_user))


def clear_auth_session() -> None:
    st.session_state.authenticated_user = None
    st.session_state.admission_progress = None
    st.session_state[SKIP_COOKIE_RESTORE_KEY] = True
    _queue_clear_cookie()


def sign_out_current_user() -> None:
    clear_auth_session()
    st.rerun()
