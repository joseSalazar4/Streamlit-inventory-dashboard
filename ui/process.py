from __future__ import annotations

from html import escape
import logging
import re
from typing import Any, Dict, Iterable, Tuple

import streamlit as st

from api.cas_api import (
    CasApiError,
    document_download_url,
    document_template_download_url,
    signed_download_url,
)
from auth.session_cookie import sign_out_current_user
from config.i18n import de
from models.file_rule import FileRule
from validators.files import (
    process_uploaded_file,
    submit_uploaded_files,
    uploader_key,
    validation_key,
)


REMOTE_FILE_STATUSES = {
    "approved",
    "pending_review",
    "needs_replacement",
    "available_for_download",
}
LOGGER = logging.getLogger(__name__)
SUPPORT_URL = "https://wa.me/4915231897485"
NAME_PART_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)
MINIMUM_STUDENT_PHASE_INDEX = 1


def format_display_name(value: object) -> str:
    name = " ".join(str(value or "").split())

    def normalize_part(match: re.Match[str]) -> str:
        part = match.group(0)
        if part.islower() or part.isupper():
            return part.capitalize()
        return part

    return NAME_PART_PATTERN.sub(normalize_part, name)


def phase_status(phase: Dict[str, Any]) -> Tuple[str, str]:
    remote_status = str(phase.get("status") or "")
    if remote_status == "approved":
        return "completed", de("Completado", "Abgeschlossen")
    if remote_status == "needs_replacement":
        return "missing", de("Requiere atención", "Aktion erforderlich")
    if remote_status == "pending_review":
        return "review", de("En revisión", "In Pruefung")
    if remote_status == "waiting_for_cas":
        return "waiting", de("Esperando a CAS", "Warten auf CAS")

    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return "completed", de("Disponible", "Verfuegbar")
    results = [
        st.session_state.validation.get(validation_key(phase["id"], rule.key), {})
        for rule in uploadable
    ]
    completed = sum(
        1
        for rule, result in zip(uploadable, results)
        if result.get("storage_status") == "saved" or rule.status in REMOTE_FILE_STATUSES
    )
    if completed == len(uploadable):
        return "completed", de("Completado", "Abgeschlossen")
    if any(result.get("ok") is False for result in results):
        return "missing", de("Requiere atención", "Aktion erforderlich")
    if any(result.get("storage_status") == "ready_to_submit" for result in results):
        return "ready", de("Listo para enviar", "Bereit zum Senden")
    return "pending", de("Pendiente", "Ausstehend")


def student_current_phase_index(phases: list[Dict[str, Any]]) -> int:
    if not phases:
        return 0
    minimum_index = min(MINIMUM_STUDENT_PHASE_INDEX, len(phases) - 1)
    for phase_index in range(minimum_index, len(phases)):
        if str(phases[phase_index].get("status") or "") != "approved":
            return phase_index
    return len(phases) - 1


def progress_metrics(phases: Iterable[Dict[str, Any]]) -> Tuple[int, int]:
    done = 0
    total = 0
    for phase in phases:
        for rule in phase["files"]:
            if not rule.can_student_upload:
                continue
            total += 1
            result = st.session_state.validation.get(validation_key(phase["id"], rule.key), {})
            if result.get("storage_status") == "saved" or rule.status in REMOTE_FILE_STATUSES:
                done += 1
    return done, total


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="brand-box">
                <div class="brand-logo-image" aria-label="CAS logo"></div>
                <div>
                    <div class="brand-title">CAS</div>
                    <div class="brand-subtitle">{de('PORTAL DE DOCUMENTOS', 'DOKUMENTENPORTAL')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        st.button(
            de("Inicio", "Uebersicht"),
            key="nav_dashboard",
            icon=":material/dashboard:",
            width="stretch",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(
            de("Cerrar sesión", "Abmelden"),
            key="nav_sign_out",
            icon=":material/logout:",
            width="stretch",
        ):
            sign_out_current_user()
        render_sidebar_help()


def render_sidebar_help() -> None:
    with st.container(key="sidebar_help_card"):
        st.markdown(
            f"""
            <div class="sidebar-help-copy">
                <div class="stat-title">{de('¿Necesitas ayuda?', 'Brauchst du Hilfe?')}</div>
                <div class="stat-meta">{de('Contacta a soporte si necesitas ayuda con un documento.', 'Kontaktiere CAS, wenn du Hilfe mit einem Dokument brauchst.')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            de("Contactar soporte", "CAS kontaktieren"),
            SUPPORT_URL,
            icon=":material/support_agent:",
            type="tertiary",
            width="content",
        )


def render_mobile_help() -> None:
    with st.container(key="mobile_help"):
        st.link_button(
            de("¿Necesitas ayuda?", "Brauchst du Hilfe?"),
            SUPPORT_URL,
            icon=":material/support_agent:",
            type="tertiary",
            width="content",
        )


def render_topbar() -> None:
    user = st.session_state.get("authenticated_user") or {}
    name = escape(format_display_name(user.get("full_name") or user.get("username") or "estudiante"))
    st.markdown(
        f"""
        <div class="greeting">
            <h1>{de('Hola', 'Hallo')}, {name}.</h1>
            <p>{de('Bienvenido de vuelta. Aquí puedes ver el estado de tu proceso de admisión.', 'Willkommen zurueck. Hier siehst du den Stand deines Aufnahmeprozesses.')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_identity() -> None:
    user = st.session_state.get("authenticated_user") or {}
    name = escape(format_display_name(user.get("full_name") or user.get("username") or "Estudiante"))
    email = escape(str(user.get("email") or ""))
    st.markdown(
        f"""
        <div class="dashboard-user">
            <div class="dashboard-brand-mark" aria-label="CAS logo"></div>
            <div class="dashboard-user-name">{name}</div>
            <div class="dashboard-user-email">{email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_card(phases: list[Dict[str, Any]]) -> None:
    done, total = progress_metrics(phases)
    percentage = 0 if total == 0 else round((done / total) * 100)
    current_phase = phases[student_current_phase_index(phases)]["number"]

    st.markdown(
        f"""
        <div class="glass-card progress-card">
            <div class="progress-head">
                <div class="progress-title">{de('Tu progreso de admisión', 'Dein Aufnahmefortschritt')}</div>
                <div class="status-chip status-ready">{de('Fase', 'Phase')} {current_phase} {de('de', 'von')} {len(phases)}</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{percentage}%;"></div>
            </div>
            <div class="progress-meta">
                <div class="tiny">{done} {de('de', 'von')} {total} {de('archivos del estudiante recibidos.', 'Dateien erhalten.')}</div>
                <div class="progress-number">{percentage}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def allowed_type_label(allowed_types: Iterable[str]) -> str:
    labels: list[str] = []
    for extension in allowed_types:
        label = "JPG" if extension.lower() in {"jpg", "jpeg"} else extension.upper()
        if label not in labels:
            labels.append(label)
    return " / ".join(labels)


def _ordered_label(order_number: int, label: str) -> str:
    return f"{order_number}. {label}"


def _css_content(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_portal_help() -> None:
    with st.container(key="portal_help_card"):
        with st.expander("Cómo usar tu portal", icon=":material/info:", expanded=False):
            st.markdown(
                """
                Aquí encontrarás los documentos necesarios para tu proceso. Abre la fase actual,
                descarga los archivos disponibles, completa o firma lo que corresponda y sube tus
                documentos terminados. Cuando subas un documento, CAS lo revisará. Si el documento
                está aprobado, no necesitas hacer nada más. Si CAS solicita una corrección, verás
                el motivo en la tarjeta del documento; corrige el archivo y vuelve a subir una
                nueva versión. <strong>Para saber qué debes hacer con cualquier documento, coloca el
                mouse sobre el símbolo de información <span class="inline-info-symbol">i</span>
                junto al nombre del documento.</strong>
                """,
                unsafe_allow_html=True,
            )


def _document_info_icon(rule: FileRule) -> str:
    items = _document_help_items(rule)
    if not items:
        return ""
    tooltip_items = "".join(
        f'<li><strong>{escape(label)}:</strong> {escape(copy)}</li>' for label, copy in items
    )
    return (
        '<span class="doc-info-icon" aria-label="Información" tabindex="0">i'
        f'<span class="doc-info-tooltip"><ul>{tooltip_items}</ul></span>'
        "</span>"
    )


def _document_help_items(rule: FileRule) -> list[tuple[str, str]]:
    items = [
        ("Qué es este documento", rule.what_is),
        ("Qué debes hacer", rule.what_to_do),
        ("Qué pasa después", rule.what_happens_next),
    ]
    return [(label, copy) for label, copy in items if copy]


def _status_message_for(rule: FileRule, result: dict[str, Any] | None) -> tuple[str, str, str] | None:
    if result:
        if result.get("storage_status") == "saved":
            return ("success", "Enviado a revisión", "CAS está revisando este documento.")
        if result.get("storage_status") == "submitting":
            return ("info", "Enviando archivo", "CAS está recibiendo tu documento.")
        if result.get("ok"):
            return (
                "warning",
                "Archivo listo para enviar",
                "Archivo seleccionado, pero aún no enviado. Haz click en Enviar archivos listos para enviarlo a CAS.",
            )
        return ("error", "", str(result.get("message") or "El archivo no se pudo validar."))
    if rule.status == "approved":
        return ("success", "Aprobado", "Documento aprobado.")
    if rule.status == "pending_review":
        return ("info", "Enviado a revisión", "CAS está revisando este documento.")
    if rule.status == "needs_replacement":
        return ("error", "Corrección solicitada", "CAS pidió una corrección. Revisa el motivo y sube una nueva versión.")
    return ("info", "Pendiente de subir", "Todavía debes subir este documento.")


def _render_status_message(kind: str, title: str, body: str) -> None:
    icon = {
        "success": "check_circle",
        "error": "report",
        "warning": "warning",
        "info": "info",
    }.get(kind, "info")
    st.markdown(
        f"""
        <div class="doc-status doc-status-{escape(kind)}">
            <span class="material-symbols-rounded">{escape(icon)}</span>
            <div>
                <div class="doc-status-title">{escape(title or body)}</div>
                {f'<div class="doc-status-copy">{escape(body)}</div>' if title else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_uploader(phase_id: str, rule: FileRule, order_number: int | None = None) -> None:
    result_key = validation_key(phase_id, rule.key)
    result = st.session_state.validation.get(result_key)
    type_label = allowed_type_label(rule.allowed_types)
    uploader_hint = _css_content(f"Máximo 200 MB por archivo • {type_label}")

    with st.container(key=f"upload_item_{phase_id}_{rule.key}"):
        st.markdown(
            f"""
            <style>
            [class*="st-key-upload_item_{phase_id}_{rule.key}"] [data-testid="stFileUploaderDropzoneInstructions"] {{
                font-size:0 !important;
                line-height:0 !important;
            }}
            [class*="st-key-upload_item_{phase_id}_{rule.key}"] [data-testid="stFileUploaderDropzoneInstructions"]::after {{
                content:"{uploader_hint}";
                display:inline-block;
                color:#718576;
                font-size:.82rem;
                line-height:1.25;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        label = escape(_ordered_label(order_number, rule.label) if order_number else rule.label)
        st.markdown(
            f"""
            <div class="upload-summary">
                <div class="upload-title-row">
                    <div class="document-title-group">
                        <div class="stat-title">{label}</div>
                        {_document_info_icon(rule)}
                    </div>
                </div>
                <div class="upload-divider"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        status_message = _status_message_for(rule, result)
        if status_message:
            _render_status_message(*status_message)
        if not result and rule.status == "needs_replacement" and rule.rejection_comment:
            st.markdown(
                f"""
                <div class="doc-status doc-status-error">
                    <span class="material-symbols-rounded">priority_high</span>
                    <div>
                        <div class="doc-status-title">{escape(de('Motivo de corrección', 'Korrekturgrund'))}</div>
                        <div class="doc-status-copy">{escape(rule.rejection_comment)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.file_uploader(
            f"{de('Subir', 'Hochladen')} {rule.label}",
            type=list(rule.allowed_types),
            key=uploader_key(phase_id, rule.key),
            help=f"{de('Máximo 200 MB. Tipos permitidos:', 'Maximal 200 MB. Erlaubte Dateitypen:')} {type_label}.",
            label_visibility="collapsed",
            on_change=process_uploaded_file,
            args=(phase_id, rule),
            width="stretch",
        )

        if result:
            st.caption(
                f"{de('Seleccionado', 'Ausgewaehlt')}: {result.get('file_name', de('archivo', 'Datei'))} "
                f"({format_file_size(int(result.get('file_size') or 0))})"
            )


def _download_rules(phase: Dict[str, Any]) -> list[FileRule]:
    return [
        rule
        for rule in phase["files"]
        if rule.flow_type == "external_link_only"
        or rule.template_scope in {"global", "student_specific"}
    ]


def _render_download_button(phase_id: str, rule: FileRule, order_number: int) -> None:
    key = f"download_{phase_id}_{rule.key}"
    label = _ordered_label(order_number, rule.label)
    if rule.flow_type == "external_link_only":
        st.link_button(
            label,
            rule.external_url or "https://hubspot.com",
            icon=":material/open_in_new:",
            width="stretch",
        )
        return
    if rule.template_scope == "global":
        if rule.template_available is False:
            st.button(
                label,
                key=key,
                icon=":material/download:",
                disabled=True,
                help=de("Esta plantilla todavía no está disponible.", "Diese Vorlage ist noch nicht verfuegbar."),
                width="stretch",
            )
            return
        _render_api_download_button(
            label,
            document_template_download_url(rule.key, scope="global"),
            f"{rule.key}.pdf",
            key,
        )
        return
    if rule.document_id:
        _render_api_download_button(label, document_download_url(rule.document_id), f"{rule.key}.pdf", key)
        return
    st.button(
        label,
        key=key,
        icon=":material/download:",
        disabled=True,
        help=de("CAS habilitará este documento cuando esté listo.", "CAS stellt dieses Dokument bereit, sobald es fertig ist."),
        width="stretch",
    )


def _render_api_download_button(label: str, url: str, file_name: str, key: str) -> None:
    _ = file_name
    st.link_button(
        label,
        signed_download_url(url, expires_in_seconds=900),
        icon=":material/download:",
        width="stretch",
    )


def _render_download_item(phase_id: str, rule: FileRule, order_number: int) -> None:
    _render_download_button(phase_id, rule, order_number)


def render_phase_downloads(phase: Dict[str, Any]) -> None:
    rules = _download_rules(phase)
    if not rules:
        return
    order_by_key = {rule.key: index for index, rule in enumerate(phase["files"], start=1)}
    with st.expander(
        de("Plantillas", "Vorlagen"),
        icon=":material/download:",
        expanded=True,
    ):
        st.caption(de("Descarga aquí los archivos que CAS habilitó para esta fase.", "Lade hier die Dateien herunter, die CAS fuer diese Phase bereitgestellt hat."))
        for row_start in range(0, len(rules), 3):
            row_rules = rules[row_start : row_start + 3]
            columns = st.columns(len(row_rules), gap="small")
            for column, rule in zip(columns, row_rules):
                with column:
                    _render_download_item(str(phase["id"]), rule, order_by_key.get(rule.key, 0))


def _phase_ready_documents(phase: Dict[str, Any]) -> list[FileRule]:
    ready: list[FileRule] = []
    for rule in phase["files"]:
        key = validation_key(phase["id"], rule.key)
        result = st.session_state.validation.get(key, {})
        if (
            rule.can_student_upload
            and result.get("ok") is True
            and result.get("storage_status") != "saved"
            and key in st.session_state.pending_uploads
        ):
            ready.append(rule)
    return ready


def render_phase_submit(phase: Dict[str, Any], placement: str) -> None:
    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return
    ready_rules = _phase_ready_documents(phase)
    with st.container(key=f"phase_submit_bar_{placement}_{phase['id']}"):
        if st.button(
            f"{de('Enviar archivos listos', 'Ausgewaehlte Dateien senden')} ({len(ready_rules)})",
            key=f"submit_phase_{placement}_{phase['id']}",
            icon=":material/cloud_upload:",
            type="primary",
            disabled=not ready_rules,
            help=de("Envía los archivos que seleccionaste.", "Sende die ausgewaehlten Dateien."),
            width="stretch",
        ):
            try:
                with st.spinner(f"{de('Enviando', 'Sende')} {len(ready_rules)} {de('archivos...', 'Dateien...')}"):
                    submit_uploaded_files(str(phase["id"]), ready_rules)
            except Exception:
                LOGGER.exception("Phase file submission failed for %s", phase["id"])
                for rule in ready_rules:
                    result = st.session_state.validation.get(
                        validation_key(phase["id"], rule.key),
                        {},
                    )
                    if result.get("storage_status") == "submitting":
                        result["storage_status"] = "ready_to_submit"
                st.error(de("Los archivos no se pudieron enviar. Inténtalo de nuevo.", "Die Dateien konnten nicht gesendet werden. Bitte versuche es erneut."))
            else:
                st.rerun()


def is_phase_unlocked(phases: list[Dict[str, Any]], phase_index: int) -> bool:
    return phase_index <= student_current_phase_index(phases)


def _toggle_phase(phase_id: str) -> None:
    st.session_state.expanded_phase = (
        "" if st.session_state.expanded_phase == phase_id else phase_id
    )


def render_phase_header(
    phases: list[Dict[str, Any]],
    phase: Dict[str, Any],
    phase_index: int,
) -> None:
    status, status_label = phase_status(phase)
    is_completed_intake = phase_index < MINIMUM_STUDENT_PHASE_INDEX
    if is_completed_intake:
        status, status_label = "completed", de("Completado", "Abgeschlossen")
    phase_id = str(phase["id"])
    unlocked = is_phase_unlocked(phases, phase_index)
    active = (
        unlocked
        and not is_completed_intake
        and st.session_state.expanded_phase == phase_id
    )
    if is_completed_intake:
        chip_text = de("Completado", "Abgeschlossen")
        status_class = "completed"
        action_icon = ":material/check_circle:"
    elif unlocked:
        chip_text = status_label if status != "pending" else de("Abrir fase", "Phase oeffnen")
        status_class = {
            "completed": "completed",
            "missing": "missing",
            "review": "waiting",
            "waiting": "waiting",
            "ready": "waiting",
            "pending": "waiting",
        }.get(status, "waiting")
        action_icon = (
            ":material/keyboard_arrow_up:"
            if active
            else ":material/keyboard_arrow_down:"
        )
    else:
        chip_text = de("Bloqueado", "Gesperrt")
        status_class = "locked"
        action_icon = ":material/lock:"

    with st.container(key=f"phase_header_{phase_id}"):
        st.markdown(
            f"""
            <div class="phase-card phase-tone-{phase['number']} {'active' if active else ''}">
                <div class="phase-head">
                    <div class="phase-left">
                        <div class="phase-badge">
                            <span class="material-symbols-rounded">{escape(str(phase["icon"]))}</span>
                        </div>
                        <div>
                            <p class="phase-title">{escape(str(phase["number"]))}. {escape(str(phase["title"]))}</p>
                            <p class="phase-desc">{escape(str(phase["subtitle"]))}</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            chip_text,
            key=f"phase_action_{status_class}_{phase_id}",
            icon=action_icon,
            disabled=is_completed_intake or not unlocked,
            help=(
                de("Esta fase está completada.", "Diese Phase ist abgeschlossen.")
                if is_completed_intake
                else
                (de("Cerrar fase", "Phase schliessen") if active else de("Abrir fase", "Phase oeffnen"))
                if unlocked
                else de("CAS desbloqueará esta fase después de aprobar la fase actual.", "CAS schaltet diese Phase frei, nachdem die aktuelle Phase genehmigt wurde.")
            ),
            on_click=_toggle_phase,
            args=(phase_id,),
        )


def render_phase_uploads(phase: Dict[str, Any]) -> None:
    render_phase_downloads(phase)
    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return
    order_by_key = {rule.key: index for index, rule in enumerate(phase["files"], start=1)}
    with st.expander(
        de("Archivos por subir", "Dateien zum Hochladen"),
        icon=":material/upload_file:",
        expanded=True,
    ):
        for row_start in range(0, len(uploadable), 2):
            row_rules = uploadable[row_start : row_start + 2]
            columns = st.columns(2, gap="medium")
            for column, rule in zip(columns, row_rules):
                with column:
                    render_document_uploader(str(phase["id"]), rule, order_by_key.get(rule.key))
        render_phase_submit(phase, "bottom")


def render_phase_card(
    phases: list[Dict[str, Any]],
    phase: Dict[str, Any],
    phase_index: int,
) -> None:
    render_phase_header(phases, phase, phase_index)
    if (
        phase_index >= MINIMUM_STUDENT_PHASE_INDEX
        and is_phase_unlocked(phases, phase_index)
        and st.session_state.expanded_phase == str(phase["id"])
    ):
        render_phase_uploads(phase)
