from __future__ import annotations

import logging
import os
from typing import Any, Dict

import streamlit as st

from api.cas_api import (
    CasApiError,
    authenticate_local_student,
    authenticate_student,
    change_password,
    get_admission_progress,
    request_password_reset,
)
from auth.session_cookie import start_auth_session
from config.i18n import de


TEST_USERNAME = "admin"
TEST_PASSWORD = "admin"
LOGGER = logging.getLogger(__name__)
SAFE_ACCOUNT_ERRORS = {
    "This portal is available to students only.",
    "Your account is not linked to a student profile. Contact support.",
    "Your account information could not be verified. Contact support.",
}

SAFE_ACCOUNT_ERRORS_ES = {
    "This portal is available to students only.": "Este portal es solo para estudiantes.",
    "Your account is not linked to a student profile. Contact support.": "Tu cuenta no está vinculada a un perfil de estudiante. Contacta a soporte.",
    "Your account information could not be verified. Contact support.": "No se pudo verificar la información de tu cuenta. Contacta a soporte.",
}


def _auth_header() -> None:
    st.markdown(
        f"""
        <div class="auth-brand">
            <div class="auth-logo">CAS</div>
            <div>
                <div class="auth-title">{de('Portal de documentos', 'Dokumentenportal')}</div>
                <div class="auth-subtitle">{de('Acceso seguro', 'Sicherer Zugang')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _student_from_login(email: str, password: str) -> tuple[Dict[str, Any], Dict[str, Any] | None]:
    test_student_id = os.environ.get("CAS_TEST_STUDENT_ID", "").strip()
    if (
        test_student_id
        and email.strip().lower() == TEST_USERNAME
        and password == TEST_PASSWORD
    ):
        payload = authenticate_local_student(test_student_id)
        user = dict(payload.get("user") or {})
        api_user_token = str(payload.get("api_user_token") or "")
        if api_user_token:
            st.session_state.api_user_token = api_user_token
            user["api_user_token"] = api_user_token
        user.setdefault("id", test_student_id)
        user.setdefault("student_id", test_student_id)
        user.setdefault("username", TEST_USERNAME)
        user.setdefault("email", "admin@local.test")
        user.setdefault(
            "full_name",
            os.environ.get("CAS_TEST_STUDENT_NAME", "Test Student").strip()
            or "Test Student",
        )
        user["is_test_user"] = True
        try:
            progress = get_admission_progress(user["student_id"])
        except CasApiError:
            progress = None
        return user, progress

    payload = authenticate_student(email, password)
    api_user_token = str(payload.get("api_user_token") or "")
    if api_user_token:
        st.session_state.api_user_token = api_user_token
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
        "api_user_token": api_user_token,
        "password_change_required": bool(api_user.get("password_change_required")),
        "password_change_token": str(payload.get("password_change_token") or ""),
    }
    return user, progress


def _render_student_sign_in() -> None:
    with st.form("student_sign_in", enter_to_submit=True, border=False):
        email = st.text_input(de("Email", "E-Mail"), key="signin_email")
        password = st.text_input(de("Contraseña", "Passwort"), type="password", key="signin_password")
        submitted = st.form_submit_button(
            de("Iniciar sesión", "Anmelden"),
            type="primary",
            icon=":material/login:",
            width="stretch",
        )

    if submitted:
        if not email or not password:
            st.error(de("Ingresa tu email y contraseña.", "Gib deine E-Mail-Adresse und dein Passwort ein."))
            return
        try:
            with st.spinner(de("Iniciando sesión...", "Anmeldung laeuft...")):
                user, progress = _student_from_login(email, password)
            user, password_change = _password_change_redirect(user, progress, email)
        except CasApiError as exc:
            LOGGER.warning("Student sign-in failed: %s", exc)
            if exc.code == "temporary_password_expired":
                st.error(de("Tu contraseña temporal expiró. Solicita una nueva contraseña.", "Dein temporaeres Passwort ist abgelaufen. Fordere ein neues Passwort an."))
            elif exc.status in {401, 403}:
                st.error(de("Email o contraseña inválidos.", "E-Mail oder Passwort ist ungueltig."))
            elif str(exc) in SAFE_ACCOUNT_ERRORS:
                st.error(de(SAFE_ACCOUNT_ERRORS_ES[str(exc)], "Dein Konto konnte nicht fuer dieses Portal bestaetigt werden. Bitte kontaktiere CAS."))
            else:
                st.error(de("No pudimos iniciar sesión en este momento. Inténtalo de nuevo.", "Die Anmeldung ist im Moment nicht moeglich. Bitte versuche es erneut."))
            return

        if password_change:
            st.session_state.pending_auth_user = password_change["user"]
            st.session_state.pending_auth_progress = password_change["progress"]
            st.session_state.pending_auth_email = password_change["email"]
            st.session_state.password_change_token = password_change["token"]
            st.session_state.auth_view = "change_password"
            st.rerun()
            return

        start_auth_session(user)
        st.session_state.pop("api_user_token", None)
        st.session_state.admission_progress = progress
        st.session_state.page = "Dashboard"
        st.rerun()
        return

    if st.button(
        de("¿Olvidaste tu contraseña?", "Passwort vergessen?"),
        key="forgot_password",
        type="tertiary",
        width="stretch",
    ):
        st.session_state.auth_view = "forgot_password"
        st.rerun()


def _password_change_redirect(
    user: Dict[str, Any],
    progress: Dict[str, Any] | None,
    submitted_email: str,
) -> tuple[Dict[str, Any], Dict[str, Any] | None]:
    authenticated_user = dict(user)
    password_change_required = bool(authenticated_user.pop("password_change_required", False))
    password_change_token = str(authenticated_user.pop("password_change_token", ""))
    if not password_change_required:
        return authenticated_user, None
    if not password_change_token:
        raise CasApiError("Password reset could not be completed. Request a new reset.")
    return authenticated_user, {
        "user": authenticated_user,
        "progress": progress,
        "email": str(authenticated_user.get("email") or submitted_email).strip().lower(),
        "token": password_change_token,
    }


def _render_forgot_password() -> None:
    with st.form("forgot_password_form", enter_to_submit=True, border=False):
        email = st.text_input(de("Email del estudiante", "E-Mail des Schuelers"), key="reset_email")
        submitted = st.form_submit_button(
            de("Enviar contraseña temporal", "Neues Passwort senden"),
            type="primary",
            icon=":material/mail:",
            width="stretch",
        )

    if submitted:
        if not email:
            st.error(de("Ingresa tu email de estudiante.", "Gib deine E-Mail-Adresse ein."))
        else:
            try:
                with st.spinner(de("Enviando contraseña temporal...", "Neues Passwort wird gesendet...")):
                    request_password_reset(email)
                st.session_state.auth_notice = (
                    de(
                        "Si existe una cuenta para ese email, se envió una contraseña temporal.",
                        "Falls ein Konto fuer diese E-Mail existiert, wurde ein temporaeres Passwort gesendet.",
                    )
                )
                st.session_state.auth_view = "sign_in"
                st.rerun()
            except CasApiError as exc:
                LOGGER.warning("Password reset request failed: %s", exc)
                st.error(de("El restablecimiento de contraseña no está disponible en este momento. Inténtalo más tarde.", "Das Zuruecksetzen des Passworts ist im Moment nicht moeglich. Bitte versuche es spaeter erneut."))

    if st.button(
        de("Volver al inicio de sesión", "Zurueck zur Anmeldung"),
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
        st.error(de("Este cambio de contraseña ya no está disponible. Solicita uno nuevo.", "Dieses temporaere Passwort ist nicht mehr verfuegbar. Fordere ein neues an."))
        if st.button(
            de("Volver al inicio de sesión", "Zurueck zur Anmeldung"),
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
            de("Nueva contraseña", "Neues Passwort"),
            type="password",
            key="new_password",
        )
        confirm_password = st.text_input(
            de("Confirmar nueva contraseña", "Neues Passwort bestaetigen"),
            type="password",
            key="confirm_new_password",
        )
        st.caption(de("Usa al menos 10 caracteres con mayúscula, minúscula y un número.", "Verwende mindestens 10 Zeichen mit Grossbuchstaben, Kleinbuchstaben und einer Zahl."))
        submitted = st.form_submit_button(
            de("Actualizar contraseña e iniciar sesión", "Passwort aktualisieren und anmelden"),
            type="primary",
            icon=":material/lock_reset:",
            width="stretch",
        )

    if submitted:
        if not new_password or not confirm_password:
            st.error(de("Ingresa y confirma tu nueva contraseña.", "Gib dein neues Passwort ein und bestaetige es."))
            return
        if new_password != confirm_password:
            st.error(de("Las contraseñas no coinciden.", "Die Passwoerter stimmen nicht ueberein."))
            return
        try:
            with st.spinner(de("Actualizando contraseña...", "Passwort wird aktualisiert...")):
                change_password(email, change_token, new_password)
        except CasApiError as exc:
            LOGGER.warning("Password change failed: %s", exc)
            if exc.code in {"weak_password", "password_unchanged"}:
                st.error(de(str(exc), "Das Passwort erfuellt die Anforderungen nicht."))
            else:
                st.error(de("Este cambio de contraseña expiró. Solicita uno nuevo.", "Dieses temporaere Passwort ist abgelaufen. Fordere ein neues an."))
            return

        progress = st.session_state.get("pending_auth_progress")
        start_auth_session(dict(pending_user))
        st.session_state.pop("api_user_token", None)
        st.session_state.admission_progress = progress
        _clear_pending_password_change()
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button(
        de("Volver al inicio de sesión", "Zurueck zur Anmeldung"),
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
                "forgot_password": de("Ingresa tu email para recibir una contraseña temporal.", "Gib deine E-Mail-Adresse ein, um ein temporaeres Passwort zu erhalten."),
                "change_password": de("Crea una nueva contraseña para terminar de iniciar sesión.", "Erstelle ein neues Passwort, um die Anmeldung abzuschliessen."),
            }
            st.caption(captions.get(auth_view, de("Inicia sesión para continuar.", "Melde dich an, um fortzufahren.")))
            notice = st.session_state.pop("auth_notice", "")
            if notice:
                st.success(notice)
            if auth_view == "forgot_password":
                _render_forgot_password()
            elif auth_view == "change_password":
                _render_change_password()
            else:
                _render_student_sign_in()
