from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import streamlit as st

from document_storage import prepare_document

st.set_page_config(
    page_title="CAS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "CAS Document Portal"


# =============================================================================
# STYLES
# Keep colors here so the visual theme can be changed without hunting through
# individual components.
# =============================================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cas-green: #1b5936;
            --cas-green-dark: #103b25;
            --cas-green-soft: #e7f3e7;
            --cas-green-hover: #d9ecd9;
            --cas-green-border: #b9d8b9;
            --cas-page: #f7f3ea;
            --cas-card: rgba(255,255,255,.84);
            --cas-soft-card: rgba(233,240,228,.80);
        }

        /* App shell */
        html, body, [class*="css"] { font-family: "Inter","Segoe UI",Arial,sans-serif; }
        .stApp { background:var(--cas-page); color:var(--cas-green-dark); }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.1rem; padding-bottom: 1rem; max-width: 1600px; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fbf7ef 0%, #f0eadf 60%, #eaf3e8 100%);
            border-right: 1px solid rgba(16, 59, 37, 0.08);
        }
        section[data-testid="stSidebar"] > div { padding-top: 1rem; }
        .brand-box {
            display:flex; align-items:center; gap:14px; padding:12px 10px 22px 10px; margin-bottom:.75rem;
        }
        .brand-logo {
            width:52px; height:52px; border-radius:16px; background:#154f31; display:grid; place-items:center;
            color:#fff; font-size:28px; box-shadow:0 10px 24px rgba(21,79,49,.18); flex-shrink:0;
        }
        .brand-title {
            font-size:1.45rem; font-weight:800; letter-spacing:.08em; color:#1a4d33;
        }
        .brand-subtitle {
            margin-top:4px; font-size:.82rem; letter-spacing:.17em; color:rgba(26,77,51,.8);
        }
        div[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(46,125,74,0.10);
            background: rgba(255,255,255,0.90);
            color: #2B5F3A;
            padding: .72rem .9rem;
            text-align: left;
            font-weight: 600;
        }

        div[data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(46,125,74,0.18);
            background: rgba(255,255,255,0.85);
            transform: translateY(-1px);
        }
        .nav-active button {
            background: linear-gradient(180deg, #e2ead7 0%, #d6e3cb 100%) !important;
            border: 1px solid rgba(21, 79, 49, 0.17) !important;
            font-weight: 700;
        }

        /* Shared cards and text */
        .glass-card, .soft-card {
            border-radius: 18px; padding: 1.2rem 1.2rem; box-shadow: 0 12px 28px rgba(57,57,57,.07);
        }
        .glass-card { background:rgba(255,255,255,.72); border:1px solid rgba(18,72,44,.08); }
        .soft-card { background:var(--cas-soft-card); border:1px solid rgba(21,79,49,.08); }
        .stat-title { font-size:1.02rem; font-weight:700; color:#194833; margin-bottom:.55rem; }
        .stat-meta { color:rgba(25,72,51,.75); font-size:.95rem; }
        .tiny { font-size:.82rem; color:rgba(24,63,43,.72); }

        /* Dashboard header */
        .greeting h1 { margin:0; font-size:2rem; line-height:1.15; color:#14432b; }
        .greeting p { margin:.2rem 0 0 0; color:rgba(20,67,43,.76); font-size:1rem; }
        .top-icons { display:flex; align-items:center; gap:.8rem; color:#194833; justify-content:flex-end; }
        .icon-pill {
            width:44px; height:44px; border-radius:50%; background:rgba(208,220,199,.75);
            display:grid; place-items:center; font-weight:700;
        }

        /* Stage header */
        .stage-card {
            background:var(--cas-card); border:1px solid rgba(17,61,39,.10);
            border-radius:16px; padding:1rem; margin-bottom:.9rem; box-shadow:0 10px 24px rgba(57,57,57,.06);
        }
        .stage-card.active {
            border:1.5px solid rgba(21,79,49,.55); box-shadow:0 10px 28px rgba(21,79,49,.10);
        }
        .stage-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; }
        .stage-left { display:flex; gap:.9rem; align-items:center; }
        .stage-badge {
            width:52px; height:52px; border-radius:50%; background:#e1ead7; display:grid; place-items:center;
            font-size:1.25rem; color:#134228; flex-shrink:0;
        }
        .stage-title { margin:0; font-size:1.03rem; color:#183f2b; font-weight:800; }
        .stage-desc { margin:.2rem 0 0 0; color:rgba(24,63,43,.78); font-size:.94rem; }
        .status-chip {
            display:inline-flex; align-items:center; gap:.35rem; border-radius:999px; padding:.32rem .7rem;
            font-size:.82rem; font-weight:700; border:1px solid transparent; white-space:nowrap;
        }
        .status-completed { background:#e0efde; color:var(--cas-green); border-color:#c0ddbd; }
        .status-missing { background:#fff0e7; color:#c85e22; border-color:#ffd1b7; }
        .status-locked { background:#fff5ee; color:#d97706; border-color:#fed7aa; }
        .status-ready { background:var(--cas-green-soft); color:var(--cas-green); border-color:var(--cas-green-border); }
        .rule-box {
            background:rgba(245,248,243,.95); border:1px dashed rgba(21,79,49,.16);
            border-radius:14px; padding:.85rem .9rem; margin-top:.75rem;
        }
        .rule-box ul { margin:.35rem 0 0 1.15rem; padding:0; }
        .rule-box li { margin:.2rem 0; }

        /* Upload cards */
        .upload-card {
            background:var(--cas-soft-card); border:1px solid rgba(21,79,49,.08);
            border-radius:16px; padding:1rem; min-height:190px; margin-top:.1rem;
            box-shadow:0 10px 24px rgba(57,57,57,.05);
        }
        .upload-card .stat-title { margin-bottom:.35rem; }
        .upload-meta {
            margin-top:.8rem; padding-top:.7rem; border-top:1px solid rgba(21,79,49,.11);
        }
        .upload-meta ul { margin:.3rem 0 .45rem 1.05rem; padding:0; }
        .upload-meta li { margin:.12rem 0; font-size:.82rem; color:rgba(24,63,43,.78); }

        /* Native Streamlit upload controls */
        .stFileUploader section {
            background:rgba(255,255,255,.85) !important; border-radius:14px !important;
            border:1px dashed rgba(21,79,49,.2) !important;
            padding:.7rem !important;
            min-height:112px !important;
        }
        .stFileUploader section button {
            background:var(--cas-green-soft) !important;
            color:var(--cas-green) !important;
            border:1px solid var(--cas-green-border) !important;
            box-shadow:none !important;
        }
        .stFileUploader section button:hover {
            background:var(--cas-green-hover) !important;
            border-color:#91be99 !important;
        }

        /* Stage arrow button and its Streamlit tooltip wrapper */
        div[data-testid="stTooltipHoverTarget"],
        div[class*="stTooltipHoverTarget"] {
            background:transparent !important;
        }
        button[data-testid="stTooltipHoverTarget"],
        button[class*="stTooltipHoverTarget"],
        [data-testid="stTooltipHoverTarget"] > button,
        [class*="stTooltipHoverTarget"] > button,
        button[title="Open stage"],
        [data-testid="stMain"] .stButton > button {
            background:var(--cas-green-soft) !important;
            color:var(--cas-green) !important;
            border:1px solid var(--cas-green-border) !important;
            box-shadow:none !important;
        }
        button[data-testid="stTooltipHoverTarget"]:hover,
        button[class*="stTooltipHoverTarget"]:hover,
        [data-testid="stTooltipHoverTarget"] > button:hover,
        [class*="stTooltipHoverTarget"] > button:hover,
        button[title="Open stage"]:hover,
        [data-testid="stMain"] .stButton > button:hover {
            background:var(--cas-green-hover) !important;
            border-color:#91be99 !important;
        }

        /* Shared Streamlit widgets */
        .stButton > button { border-radius:12px; border:none; padding:.68rem 1rem; font-weight:700; }
        .stProgress > div > div > div > div { background-color:var(--cas-green) !important; }
        @media (max-width: 900px) { .greeting h1 { font-size:1.6rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


@dataclass
class FileRule:
    label: str
    key: str
    required_fields: List[str]
    description: str


# =============================================================================
# PROCESS CONFIGURATION
# Each block below defines the three PDF requirements for one student step.
# =============================================================================
STAGES: List[Dict[str, Any]] = [
    # STEP 1: Identity Verification
    {
        "id": 1,
        "title": "Identity Verification",
        "subtitle": "Validación de identidad y datos básicos.",
        "icon": "🪪",
        "files": [
            FileRule("info_basica", "info_basica", ["nombre", "apellido"], "Debe contener nombre y apellido."),
            FileRule("documento_identidad", "documento_identidad", ["numero_identificacion", "fecha_nacimiento"], "Debe contener número de identificación y fecha de nacimiento."),
            FileRule("selfie_verificacion", "selfie_verificacion", [], "PDF de verificación. No requiere campos de texto específicos."),
        ],
    },
    # STEP 2: Proof of Address
    {
        "id": 2,
        "title": "Proof of Address",
        "subtitle": "Comprobante de domicilio y validaciones de dirección.",
        "icon": "🏠",
        "files": [
            FileRule("comprobante_direccion", "comprobante_direccion", ["direccion", "pais"], "Debe incluir dirección completa y país."),
            FileRule("estado_cuenta", "estado_cuenta", ["nombre_titular", "direccion"], "Debe mostrar titular y dirección."),
            FileRule("recibo_servicio", "recibo_servicio", ["fecha_emision", "direccion"], "Debe incluir fecha de emisión y dirección."),
        ],
    },
    # STEP 3: Contract / Agreement
    {
        "id": 3,
        "title": "Contract / Agreement",
        "subtitle": "Firma y condiciones de la relación contractual.",
        "icon": "✍️",
        "files": [
            FileRule("contrato_firmado", "contrato_firmado", ["firma", "nombre_completo"], "Debe contener firma y nombre completo."),
            FileRule("anexo_terminos", "anexo_terminos", ["terminos", "condiciones"], "Debe incluir términos y condiciones."),
            FileRule("consentimiento", "consentimiento", ["consentimiento_explicito"], "Debe declarar consentimiento explícito."),
        ],
    },
    # STEP 4: Financial Information
    {
        "id": 4,
        "title": "Financial Information",
        "subtitle": "Información financiera y soportes bancarios.",
        "icon": "📈",
        "files": [
            FileRule("reporte_financiero", "reporte_financiero", ["ingresos", "egresos"], "Debe contener ingresos y egresos."),
            FileRule("datos_bancarios", "datos_bancarios", ["cuenta", "banco"], "Debe contener banco y número de cuenta."),
            FileRule("declaracion_tributaria", "declaracion_tributaria", ["impuestos", "periodo"], "Debe incluir impuestos y periodo."),
        ],
    },
    # STEP 5: Final Review
    {
        "id": 5,
        "title": "Final Review",
        "subtitle": "Revisión final del equipo.",
        "icon": "🏁",
        "files": [
            FileRule("resumen_final", "resumen_final", ["aprobacion", "estado_final"], "Debe contener aprobación y estado final."),
            FileRule("checklist_final", "checklist_final", ["item", "verificado"], "Checklist final con items verificados."),
            FileRule("cierre_proceso", "cierre_proceso", ["cierre", "fecha"], "Debe incluir cierre y fecha."),
        ],
    },
]


# =============================================================================
# SESSION STATE
# =============================================================================
def init_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("expanded_stage", 0)
    st.session_state.setdefault("validation", {})
    st.session_state.setdefault("pending_uploads", {})


# =============================================================================
# PDF VALIDATION
# =============================================================================
class PdfExtractionError(RuntimeError):
    pass


def safe_ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower().strip() if "." in name else ""


def _bytes_to_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader
            from PyPDF2.errors import PdfReadError
        except ModuleNotFoundError as exc:
            raise PdfExtractionError(
                "Falta la dependencia para leer PDFs. Instala requirements.txt."
            ) from exc

    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
    except PdfReadError as exc:
        raise PdfExtractionError(
            "El archivo no tiene una estructura PDF válida."
        ) from exc
    except Exception as exc:
        raise PdfExtractionError(
            f"No se pudo abrir el PDF ({type(exc).__name__})."
        ) from exc

    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception:
            unlocked = 0
        if not unlocked:
            raise PdfExtractionError("El PDF está protegido con contraseña.")

    extracted_parts: List[str] = []
    page_errors: List[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            if text:
                extracted_parts.append(text)
        except Exception as exc:
            page_errors.append(f"página {page_number}: {type(exc).__name__}")

    # Form fields are optional. Failure here must not invalidate readable text.
    try:
        form_fields = reader.get_fields() or {}
        for field_name, field_data in form_fields.items():
            value = field_data.get("/V")
            if value not in (None, ""):
                extracted_parts.append(f"{field_name}: {value}")
    except Exception:
        pass

    if not extracted_parts and page_errors:
        raise PdfExtractionError(
            "No se pudo extraer texto del PDF (" + "; ".join(page_errors) + ")."
        )

    return "\n".join(extracted_parts)


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("_", " ")
    value = re.sub(r"[ \t]+", " ", value)
    return value


def _field_label_pattern(field: str) -> str:
    words = re.findall(r"[a-z0-9]+", _normalize_text(field))
    separator = r"[\s_-]+(?:(?:de|del|la|el)[\s_-]+)?"
    patterns = []
    for word in words:
        plural_suffix = "" if word.endswith("s") else "s?"
        patterns.append(re.escape(word) + plural_suffix)
    return separator.join(patterns)


def _has_filled_field(text: str, field: str, all_fields: List[str]) -> bool:
    normalized = _normalize_text(text)
    field_pattern = _field_label_pattern(field)
    other_labels = [
        _field_label_pattern(other)
        for other in all_fields
        if _normalize_text(other) != _normalize_text(field)
    ]
    stop_pattern = "|".join(other_labels)
    lookahead = rf"(?=\n|{stop_pattern}\s*[:\-]|\Z)" if stop_pattern else r"(?=\n|\Z)"
    pattern = re.compile(
        rf"\b{field_pattern}\b\s*(?:[:=\-]\s*)?(.*?){lookahead}",
        re.IGNORECASE,
    )

    for match in pattern.finditer(normalized):
        candidate = match.group(1).strip()
        candidate = re.sub(r"^[.\-–—:/\\\s]+|[.\-–—:/\\\s]+$", "", candidate)
        if re.search(r"[a-z0-9]", candidate):
            return True
    return False


def validate_pdf(file_name: str, data: bytes, rule: FileRule) -> Tuple[bool, str]:
    ext = safe_ext(file_name)
    if ext != "pdf":
        return False, f"Extensión .{ext or 'sin extensión'} no permitida. Por ahora solo se aceptan archivos PDF."

    try:
        text = _bytes_to_text(data)
        if not text.strip():
            return False, "No se encontró texto seleccionable en el PDF. Los PDFs escaneados requieren OCR."
        if not rule.required_fields:
            return True, "PDF válido y con texto detectable."

        missing = [
            field
            for field in rule.required_fields
            if not _has_filled_field(text, field, rule.required_fields)
        ]
        if missing:
            return False, f"Campos vacíos o no detectados: {', '.join(missing)}"
        return True, f"PDF válido. Campos completos: {', '.join(rule.required_fields)}"
    except PdfExtractionError as exc:
        return False, str(exc)


def uploader_key(stage_id: int, rule_key: str) -> str:
    return f"u_{stage_id}_{rule_key}"


def validation_key(stage_id: int, rule_key: str) -> Tuple[int, str]:
    return stage_id, rule_key


def process_uploaded_file(stage_id: int, rule: FileRule) -> None:
    """Prepare and validate the selected PDF, then persist it across reruns."""
    widget_key = uploader_key(stage_id, rule.key)
    result_key = validation_key(stage_id, rule.key)
    uploaded_file = st.session_state.get(widget_key)

    if uploaded_file is None:
        st.session_state.validation.pop(result_key, None)
        st.session_state.pending_uploads.pop(result_key, None)
        return

    data = uploaded_file.getvalue()
    document = prepare_document(
        stage_id=stage_id,
        document_key=rule.key,
        file_name=uploaded_file.name,
        content_type=getattr(uploaded_file, "type", None) or "application/pdf",
        data=data,
    )
    st.session_state.pending_uploads[result_key] = document

    ok, message = validate_pdf(document.file_name, document.data, rule)
    st.session_state.validation[result_key] = {
        "ok": ok,
        "message": message,
        "file_name": document.file_name,
        "file_size": document.size,
        "sha256": document.sha256,
        "progress": 100,
        "storage_status": "ready" if ok else "blocked",
    }


# =============================================================================
# PROCESS STATUS AND UI
# =============================================================================
def stage_status(stage: Dict[str, Any]) -> Tuple[str, str]:
    status_list = [
        st.session_state.validation.get((stage["id"], rule.key), {}).get("ok")
        for rule in stage["files"]
    ]
    if all(v is True for v in status_list):
        return "completed", "Completed"
    if any(v is False for v in status_list):
        return "missing", "Requires attention"
    return "locked", "Pending"


def progress_metrics() -> Tuple[int, int]:
    total = done = 0
    for stage in STAGES:
        for rule in stage["files"]:
            total += 1
            res = st.session_state.validation.get((stage["id"], rule.key))
            if res and res.get("ok") is True:
                done += 1
    return done, total


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-box">
                <div class="brand-logo">✈</div>
                <div>
                    <div class="brand-title">CAS</div>
                    <div class="brand-subtitle">DOCUMENT PORTAL</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        pages = ["Dashboard", "Uploads", "Profile", "Help & Support", "Logout"]
        icons = {"Dashboard": "🏠", "Uploads": "📤", "Profile": "👤", "Help & Support": "🎧", "Logout": "↩️"}
        for page in pages:
            cls = "nav-active" if st.session_state.page == page else ""
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(f"{icons[page]}   {page}", key=f"nav_{page}"):
                st.session_state.page = page
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="soft-card">
                <div class="stat-title">Your information is secure with us.</div>
                <div class="stat-meta">Encryption and access control for documents.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_topbar() -> None:
    left, right = st.columns([8.5, 2.5], vertical_alignment="center")
    with left:
        st.markdown(
            """
            <div class="greeting">
                <h1>Hello, Gabo Blanco!</h1>
                <p>Welcome back! Here's the status of your process.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="top-icons">
                <div style="font-size:1.2rem;">🔔</div>
                <div class="icon-pill">GB</div>
                <div style="font-weight:600;">Gabo Blanco</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_status_panel() -> None:
    done, total = progress_metrics()
    pct = 0 if total == 0 else round((done / total) * 100)
    c1, c2 = st.columns([8, 4], gap="large", vertical_alignment="top")
    with c1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem;">
                    <div class="stat-title">Your Process Progress</div>
                    <div class="status-chip status-completed">Step {min(done+2 // 3 + 1, 5)} of 5</div>
                </div>
                <div style="height:12px; margin:.9rem 0 .5rem 0; background:#e7eadf; border-radius:999px; overflow:hidden;">
                    <div style="width:{20}%; height:100%; background:linear-gradient(90deg, #1d5a39 0%, #134228 100%); border-radius:999px;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="tiny">Please upload all required documents to move forward.</div>
                    <div style="font-weight:800; color:#18402a;">{pct+20}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
        """
        <div class="soft-card">
            <div class="stat-title">Need Help?</div>
            <div class="stat-meta">Contact our support team on WhatsApp.</div>
            <div style="margin-top:.9rem;">
                <a href="https://www.facebook.com/cascostarica1" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; border:none; border-radius:14px; padding:.8rem .9rem; background:white; color:#134228; font-weight:700; box-shadow:0 8px 18px rgba(0,0,0,.06); cursor:pointer;">
                        💬 Chat on Facebook
                    </button>
                </a>
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


def render_document_uploader(stage_id: int, rule: FileRule) -> None:
    """Render one document requirement, upload progress, and validation result."""
    result_key = validation_key(stage_id, rule.key)
    result = st.session_state.validation.get(result_key)
    fields = rule.required_fields or ["Sin campos de texto requeridos"]

    st.markdown(
        f"""
        <div class="upload-card">
            <div class="stat-title">{rule.label}</div>
            <div class="tiny">{rule.description}</div>
            <div class="upload-meta">
                <div class="tiny"><b>Required information:</b></div>
                <ul>{''.join([f'<li>{field.replace("_", " ")}</li>' for field in fields])}</ul>
                <div class="tiny"><b>Available format:</b> PDF</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result:
        file_size = format_file_size(result.get("file_size", 0))
        st.caption(f"Loaded: {result['file_name']} ({file_size})")
        st.progress(result.get("progress", 100))
    else:
        st.caption("Waiting for PDF")
        st.progress(0)

    st.file_uploader(
        f"Upload {rule.label}",
        type=["pdf"],
        key=uploader_key(stage_id, rule.key),
        label_visibility="collapsed",
        on_change=process_uploaded_file,
        args=(stage_id, rule),
    )

    if result:
        if result["ok"]:
            st.success(result["message"])
        else:
            st.error(result["message"])


def render_stage_header(stage: Dict[str, Any]) -> None:
    stage_id = stage["id"]
    status, _ = stage_status(stage)
    active = st.session_state.expanded_stage == stage_id
    status_class = {"completed": "status-completed", "missing": "status-missing", "locked": "status-locked"}[status]
    unlocked = is_stage_unlocked(stage_id)

    if status == "completed":
        chip_text = "Completed ✓"
        status_class = "status-completed"

    elif unlocked:
        chip_text = "Ready to upload 📤"
        status_class = "status-ready"

    else:
        chip_text = "Locked 🔒"
        status_class = "status-locked"

    c1, c2 = st.columns([11, 1], vertical_alignment="center")
    with c1:
        st.markdown(
            f"""
            <div class="stage-card {'active' if active else ''}">
                <div class="stage-head">
                    <div class="stage-left">
                        <div class="stage-badge">{stage["icon"]}</div>
                        <div>
                            <p class="stage-title">{stage_id}. {stage["title"]}</p>
                            <p class="stage-desc">{stage["subtitle"]}</p>
                        </div>
                    </div>
                    <span class="status-chip {status_class}">{chip_text}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    unlocked = is_stage_unlocked(stage_id)

    with c2:
        if st.button(
            "›",
            key=f"toggle_{stage_id}",
            disabled=not unlocked,
            help="Open stage" if unlocked else "Complete the previous step first",
        ):
            st.session_state.expanded_stage = 0 if active else stage_id


def render_stage_uploads(stage: Dict[str, Any]) -> None:
    stage_id = stage["id"]
    st.markdown(
        """
        <div class="rule-box">
            <div class="stat-title" style="margin-bottom:.3rem;">Sube 3 archivos de esta etapa</div>
            <div class="tiny">Cada archivo se revisa con reglas diferentes según la etapa y el tipo de documento.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3, gap="medium")
    for column, rule in zip(cols, stage["files"]):
        with column:
            render_document_uploader(stage_id, rule)
    st.markdown("<br>", unsafe_allow_html=True)


def render_stage_card(stage: Dict[str, Any]) -> None:
    render_stage_header(stage)

    active = st.session_state.expanded_stage == stage["id"]
    if active:
        render_stage_uploads(stage)


def is_stage_unlocked(stage_id: int) -> bool:
    if stage_id == 1:
        return True

    previous_stage = STAGES[stage_id - 2]  # stage IDs start at 1
    status, _ = stage_status(previous_stage)

    return status == "completed"


def dashboard_page() -> None:
    render_topbar()
    st.write("")
    render_status_panel()
    st.write("")
    left, right = st.columns([8.6, 3.4], gap="large", vertical_alignment="top")
    with left:
        st.markdown("## Process Steps")
        for stage in STAGES:
            render_stage_card(stage)
    with right:
        # render_process_summary()
        st.write("")
        st.markdown(
            """
            <div class="soft-card">
                <div class="stat-title">Your data is protected</div>
                <div class="stat-meta">We use High-level encryption to keep your documents safe.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def uploads_page() -> None:
    st.markdown("## Upload Center")
    st.caption("Aquí puedes revisar y subir documentos por etapa. La validación se ejecuta al instante.")
    for stage in STAGES:
        with st.expander(f"{stage['id']}. {stage['title']}", expanded=(st.session_state.expanded_stage == stage["id"])):
            render_stage_card(stage)


def profile_page() -> None:
    st.markdown("## Profile")
    st.info("Sección lista para editar datos del usuario, permisos y datos de contacto.")


def help_page() -> None:
    st.markdown("## Help & Support")
    st.success("Puedes agregar aquí FAQs, soporte por Facebook, correo y tickets.")


def logout_page() -> None:
    st.markdown("## Logout")
    st.warning("Aquí puedes cerrar sesión, limpiar estado o redirigir al login.")


def main() -> None:
    inject_css()
    init_state()
    render_sidebar()
    page = st.session_state.page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Uploads":
        uploads_page()
    elif page == "Profile":
        profile_page()
    elif page == "Help & Support":
        help_page()
    elif page == "Logout":
        logout_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
