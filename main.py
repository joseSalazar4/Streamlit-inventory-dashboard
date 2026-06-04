from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import streamlit as st

st.set_page_config(
    page_title="CAS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "CAS Document Portal"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] { font-family: "Inter","Segoe UI",Arial,sans-serif; }
        .stApp {
            background: linear-gradient(180deg, #fbf8f1 0%, #faf7f0 0%, #f7f3ea 0%);
            color: #103b25;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.1rem; padding-bottom: 1rem; max-width: 1600px; }

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
            border: 1px solid rgba(46,125,74,0.10); /* subtle green border */
            background: background: background: rgba(255,255,255,0.90);

                                           /* lighter background */
            color: #2B5F3A;                         /* softer green text */
            padding: .72rem .9rem;
            text-align: left;
            font-weight: 600;
        }

        div[data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(46,125,74,0.18);
            background: rgba(255,255,255,0.85);     /* slightly brighter on hover */
            transform: translateY(-1px);
        }

        .nav-active button {
            background: linear-gradient(180deg, #e2ead7 0%, #d6e3cb 100%) !important;
            border: 1px solid rgba(21, 79, 49, 0.17) !important;
            font-weight: 700;
        }
        .glass-card, .soft-card {
            border-radius: 18px; padding: 1.2rem 1.2rem; box-shadow: 0 12px 28px rgba(57,57,57,.07);
        }
        .glass-card {
            background: rgba(255,255,255,.72); border:1px solid rgba(18,72,44,.08);
        }
        .soft-card {
            background: rgba(233,240,228,.80); border:1px solid rgba(21,79,49,.08);
        }
        .stat-title { font-size:1.02rem; font-weight:700; color:#194833; margin-bottom:.55rem; }
        .stat-meta { color:rgba(25,72,51,.75); font-size:.95rem; }
        .greeting h1 { margin:0; font-size:2rem; line-height:1.15; color:#14432b; }
        .greeting p { margin:.2rem 0 0 0; color:rgba(20,67,43,.76); font-size:1rem; }
        .top-icons { display:flex; align-items:center; gap:.8rem; color:#194833; justify-content:flex-end; }
        .icon-pill {
            width:44px; height:44px; border-radius:50%; background:rgba(208,220,199,.75);
            display:grid; place-items:center; font-weight:700;
        }
        .stage-card {
            background:rgba(255,255,255,.84); border:1px solid rgba(17,61,39,.10);
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
        .status-completed {
    background:#e0efde;
    color:#1b5936;
    border-color:#c0ddbd;
}

.status-missing {
    background:#fff0e7;
    color:#c85e22;
    border-color:#ffd1b7;
}

.status-locked {
    background:#fff5ee;
    color:#d97706;
    border-color:#fed7aa;
}

.status-ready {
    background:#e7f3e7;
    color:#1b5936;
    border-color:#b9d8b9;
}
        .rule-box {
            background:rgba(245,248,243,.95); border:1px dashed rgba(21,79,49,.16);
            border-radius:14px; padding:.85rem .9rem; margin-top:.75rem;
        }
        .rule-box ul { margin:.35rem 0 0 1.15rem; padding:0; }
        .rule-box li { margin:.2rem 0; }
        .timeline { position:relative; padding-left:1.15rem; }
        .timeline::before {
            content:""; position:absolute; left:.38rem; top:.2rem; bottom:.2rem; width:2px;
            background:rgba(21,79,49,.14);
        }
        .timeline-item { position:relative; margin-bottom:.9rem; padding-left:.55rem; }
        .timeline-item::before {
            content:""; position:absolute; left:-.02rem; top:.24rem; width:.72rem; height:.72rem; border-radius:50%;
            background:#dfe8d8; border:2px solid #b8cdb2;
        }
        .timeline-item.done::before { background:#1b5936; border-color:#1b5936; }
        .timeline-name { font-weight:700; color:#163f2a; }
        .timeline-sub { font-size:.88rem; color:rgba(22,63,42,.68); }
        .tiny { font-size:.82rem; color:rgba(24,63,43,.72); }
        .stFileUploader label { color:#18402a !important; font-weight:600 !important; }
        .stFileUploader section {
            background:rgba(255,255,255,.85) !important; border-radius:14px !important;
            border:1px dashed rgba(21,79,49,.2) !important;
        }
        .stButton > button { border-radius:12px; border:none; padding:.68rem 1rem; font-weight:700; }
        @media (max-width: 900px) { .greeting h1 { font-size:1.6rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


@dataclass
class FileRule:
    label: str
    key: str
    accepted_ext: List[str]
    required_fields: List[str]
    description: str
    mode: str = "contains"  # contains | image_only | top_level_keys


STAGES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Identity Verification",
        "subtitle": "Validación de identidad y datos básicos.",
        "icon": "🪪",
        "files": [
            FileRule("info_basica", "info_basica", ["json", "csv", "txt"], ["nombre", "apellido"], "Debe contener nombre y apellido."),
            FileRule("documento_identidad", "documento_identidad", ["pdf", "png", "jpg", "jpeg", "docx"], ["numero_identificacion", "fecha_nacimiento"], "Debe contener número de identificación y fecha de nacimiento."),
            FileRule("selfie_verificacion", "selfie_verificacion", ["jpg", "jpeg", "png"], [], "Imagen de selfie clara. No se valida contenido textual.", "image_only"),
        ],
    },
    {
        "id": 2,
        "title": "Proof of Address",
        "subtitle": "Comprobante de domicilio y validaciones de dirección.",
        "icon": "🏠",
        "files": [
            FileRule("comprobante_direccion", "comprobante_direccion", ["pdf", "txt", "csv", "docx"], ["direccion", "pais"], "Debe incluir dirección completa y país."),
            FileRule("estado_cuenta", "estado_cuenta", ["pdf", "csv", "txt"], ["nombre_titular", "direccion"], "Debe mostrar titular y dirección."),
            FileRule("recibo_servicio", "recibo_servicio", ["pdf", "png", "jpg", "jpeg", "docx"], ["fecha_emision", "direccion"], "Debe incluir fecha de emisión y dirección."),
        ],
    },
    {
        "id": 3,
        "title": "Contract / Agreement",
        "subtitle": "Firma y condiciones de la relación contractual.",
        "icon": "✍️",
        "files": [
            FileRule("contrato_firmado", "contrato_firmado", ["pdf", "docx"], ["firma", "nombre_completo"], "Debe contener firma y nombre completo."),
            FileRule("anexo_terminos", "anexo_terminos", ["pdf", "txt", "docx"], ["terminos", "condiciones"], "Debe incluir términos y condiciones."),
            FileRule("consentimiento", "consentimiento", ["pdf", "txt", "csv"], ["consentimiento_explicito"], "Debe declarar consentimiento explícito."),
        ],
    },
    {
        "id": 4,
        "title": "Financial Information",
        "subtitle": "Información financiera y soportes bancarios.",
        "icon": "📈",
        "files": [
            FileRule("reporte_financiero", "reporte_financiero", ["pdf", "csv", "xlsx", "txt"], ["ingresos", "egresos"], "Debe contener ingresos y egresos."),
            FileRule("datos_bancarios", "datos_bancarios", ["pdf", "csv", "txt", "xlsx"], ["cuenta", "banco"], "Debe contener banco y número de cuenta."),
            FileRule("declaracion_tributaria", "declaracion_tributaria", ["pdf", "docx", "txt"], ["impuestos", "periodo"], "Debe incluir impuestos y periodo."),
        ],
    },
    {
        "id": 5,
        "title": "Final Review",
        "subtitle": "Revisión final del equipo.",
        "icon": "🏁",
        "files": [
            FileRule("resumen_final", "resumen_final", ["pdf", "docx", "txt"], ["aprobacion", "estado_final"], "Debe contener aprobación y estado final."),
            FileRule("checklist_final", "checklist_final", ["pdf", "csv", "txt"], ["item", "verificado"], "Checklist final con items verificados."),
            FileRule("cierre_proceso", "cierre_proceso", ["pdf", "txt", "docx"], ["cierre", "fecha"], "Debe incluir cierre y fecha."),
        ],
    },
]


def init_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("expanded_stage", 0)
    st.session_state.setdefault("validation", {})


def safe_ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower().strip() if "." in name else ""


def _bytes_to_text(data: bytes) -> str:
    """
    Extrae texto únicamente desde PDFs.
    """

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))

        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return "\n".join(pages).lower()

    except Exception as exc:
        raise RuntimeError(
            "No se pudo leer el PDF. Verifica que no esté protegido o corrupto."
        ) from exc
    
def validate_uploaded_file(uploaded_file, rule: FileRule) -> Tuple[bool, str]:
    ext = safe_ext(uploaded_file.name)
    if ext not in rule.accepted_ext:
        return False, f"Extensión .{ext or 'sin extensión'} no permitida. Permitidas: {', '.join(rule.accepted_ext)}"
    if rule.mode == "image_only":
        return True, "Archivo de imagen recibido. Validación textual no aplica."
    raw = uploaded_file.getvalue()
    try:
        if ext == "json":
            content = json.loads(raw.decode("utf-8", errors="ignore"))
            flat_text = json.dumps(content, ensure_ascii=False).lower()
            missing = [f for f in rule.required_fields if f.lower() not in flat_text]
            return (len(missing) == 0, "JSON válido y con campos requeridos." if not missing else f"Faltan campos o valores relacionados: {', '.join(missing)}")
        if ext == "csv":
            text = raw.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(text))
            headers = [h.strip().lower() for h in (reader.fieldnames or [])]
            missing = [f for f in rule.required_fields if f.lower() not in headers]
            return (len(missing) == 0, "CSV válido y con columnas requeridas." if not missing else f"Faltan columnas: {', '.join(missing)}")
        text = _bytes_to_text(raw).lower()
        missing = [f for f in rule.required_fields if f.lower() not in text]
        return (len(missing) == 0, f"Archivo válido. Se encontraron los campos requeridos: {', '.join(rule.required_fields)}" if not missing else f"Faltan campos detectables en el contenido: {', '.join(missing)}")
    except json.JSONDecodeError:
        return False, "El archivo JSON no tiene un formato válido."
    except Exception as exc:
        return False, str("")


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


def render_process_summary() -> None:
    st.markdown('<div class="glass-card"><div class="stat-title">Process Summary</div><div class="timeline">', unsafe_allow_html=True)
    for stage in STAGES:
        status, _ = stage_status(stage)
        done_cls = "done" if status == "completed" else ""
        subtitle = "Completed on May 15, 2024" if stage["id"] == 1 else ("Completed" if status == "completed" else ("Missing document" if status == "missing" else "Locked"))
        st.markdown(
            f"""
            <div class="timeline-item {done_cls}">
                <div class="timeline-name">{stage['title']}</div>
                <div class="timeline-sub">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_stage_card(stage: Dict[str, Any]) -> None:
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
    if active:
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
        for idx, rule in enumerate(stage["files"]):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="soft-card" style="min-height: 350px;">
                        <div class="stat-title">{rule.label}</div>
                        <div class="tiny">{rule.description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                uploaded = st.file_uploader(
                    f"A",
                    type=["pdf"],
                    key=f"u_{stage_id}_{rule.key}",
                    label_visibility="visible",
                )
                if uploaded is not None:
                    ok, msg = validate_uploaded_file(uploaded, rule)
                    st.session_state.validation[(stage_id, rule.key)] = {"ok": ok, "message": msg, "file_name": uploaded.name}
                    st.success(msg) if ok else st.error(msg)
                result = st.session_state.validation.get((stage_id, rule.key))
                if result:
                    st.caption(("✅ " if result["ok"] else "❌ ") + result["file_name"])
                else:
                    st.caption("Upload File to start checking.")
                st.markdown(
                    f"""
                    <div class="rule-box">
                        <div class="tiny"><b>Required information:</b></div>
                        <ul>{''.join([f'<li>{field}</li>' for field in (rule.required_fields or ['Sin campos de texto'])])}</ul>
                        <div class="tiny" style="margin-top:.35rem;"><b>Formatos:</b> {', '.join(rule.accepted_ext)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)

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
    st.success("Puedes agregar aquí FAQs, soporte por WhatsApp, correo y tickets.")


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
