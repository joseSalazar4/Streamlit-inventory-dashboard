from __future__ import annotations

import json
from typing import Any, Dict

import streamlit as st

from auth.server_session import session_store

COOKIE_NAME = "cas_student_session"
PENDING_SESSION_KEY = "_cas_session_handoff"
LOGOUT_PENDING_KEY = "_cas_logout_pending"
SKIP_COOKIE_RESTORE_KEY = "_cas_skip_cookie_restore"

def _clean_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": str(user.get("id") or user.get("student_id") or ""), "student_id": str(user.get("student_id") or user.get("id") or ""), "username": str(user.get("username") or user.get("email") or ""), "full_name": str(user.get("full_name", "")), "email": str(user.get("email", "")), "user_type": "student", "is_test_user": bool(user.get("is_test_user")), "api_user_token": str(user.get("api_user_token", ""))}

def _session_id() -> str:
    try: return str(st.context.cookies.get(COOKIE_NAME, ""))
    except Exception: return ""

def render_cookie_update() -> None:
    ticket, logout = st.session_state.pop(PENDING_SESSION_KEY, ""), st.session_state.pop(LOGOUT_PENDING_KEY, False)
    if not ticket and not logout: return
    method = "DELETE" if logout else "POST"
    body = "" if logout else f", body: JSON.stringify({json.dumps({'ticket': ticket})})"
    st.html(f"<script>(async()=>{{await fetch('/_cas/session',{{method:'{method}',credentials:'same-origin',headers:{{'Content-Type':'application/json'}}{body}}});try{{window.parent.location.reload()}}catch(_){{window.location.reload()}}}})();</script>", unsafe_allow_javascript=True)

def restore_auth_session() -> None:
    if st.session_state.pop(SKIP_COOKIE_RESTORE_KEY, False) or st.session_state.get("authenticated_user"): return
    user = session_store().get(_session_id()) if _session_id() else None
    if user and user.get("user_type") == "student": st.session_state.authenticated_user = _clean_user(user)
    elif _session_id(): st.session_state[LOGOUT_PENDING_KEY] = True

def start_auth_session(user: Dict[str, Any]) -> None:
    user = _clean_user(user); st.session_state.authenticated_user = user
    store = session_store(); st.session_state[PENDING_SESSION_KEY] = store.issue_ticket(store.create(user))

def clear_auth_session() -> None:
    if _session_id(): session_store().revoke(_session_id())
    st.session_state.authenticated_user = None; st.session_state.admission_progress = None; st.session_state[SKIP_COOKIE_RESTORE_KEY] = True; st.session_state[LOGOUT_PENDING_KEY] = True

def sign_out_current_user() -> None:
    clear_auth_session(); st.rerun()
