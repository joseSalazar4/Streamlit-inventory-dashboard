from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "CAS_student_portal_current_capabilities.pdf"
LOGO = ROOT / "assets" / "cas-logo-navbar.png"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 16 * mm
MARGIN_TOP = 15 * mm
MARGIN_BOTTOM = 15 * mm

INK = colors.HexColor("#173B2A")
GREEN = colors.HexColor("#1B5936")
GREEN_DARK = colors.HexColor("#103B25")
SAGE = colors.HexColor("#E7F3E7")
CREAM = colors.HexColor("#F7F3EA")
PAPER = colors.HexColor("#FFFDF8")
BLUE = colors.HexColor("#2C6685")
BLUE_SOFT = colors.HexColor("#EAF3F7")
GOLD_SOFT = colors.HexColor("#FFF4DE")
ROSE_SOFT = colors.HexColor("#FCEDEF")
LINE = colors.HexColor("#C9D8CF")
MUTED = colors.HexColor("#5A7063")
WHITE = colors.white


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=29,
        textColor=WHITE,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=14,
        textColor=colors.HexColor("#DDEBE3"),
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=GREEN_DARK,
        spaceBefore=2,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.6,
        leading=13,
        textColor=GREEN,
        spaceBefore=4,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCompact",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.2,
        textColor=INK,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.2,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="Tiny",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=6.8,
        leading=8.8,
        textColor=MUTED,
    )
)
styles.add(
    ParagraphStyle(
        name="Metric",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=18,
        textColor=GREEN_DARK,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricLabel",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="StepNumber",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=WHITE,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="StepTitle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=11.5,
        textColor=GREEN_DARK,
        spaceAfter=1,
    )
)
styles.add(
    ParagraphStyle(
        name="StepBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.7,
        leading=10.2,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHead",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.4,
        leading=9,
        textColor=WHITE,
    )
)
styles.add(
    ParagraphStyle(
        name="TableCell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.1,
        leading=9,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="TableCellStrong",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9,
        textColor=GREEN_DARK,
    )
)
styles.add(
    ParagraphStyle(
        name="CodeCell",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=6.6,
        leading=8.5,
        textColor=BLUE,
    )
)
styles.add(
    ParagraphStyle(
        name="Route",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=6.5,
        leading=8.5,
        textColor=GREEN_DARK,
    )
)
styles.add(
    ParagraphStyle(
        name="Footer",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=6.8,
        leading=8,
        textColor=MUTED,
    )
)
styles.add(
    ParagraphStyle(
        name="FooterPage",
        parent=styles["Footer"],
        alignment=TA_RIGHT,
    )
)


def p(text: str, style: str = "BodyCompact") -> Paragraph:
    return Paragraph(text, styles[style])


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.45)
    canvas.line(MARGIN_X, 11 * mm, PAGE_WIDTH - MARGIN_X, 11 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.8)
    canvas.drawString(MARGIN_X, 7.5 * mm, "CAS Student Document Portal | Current code overview")
    canvas.drawRightString(
        PAGE_WIDTH - MARGIN_X,
        7.5 * mm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def title_banner() -> Table:
    logo = Image(str(LOGO), width=49 * mm, height=13.5 * mm)
    copy = [
        p("Student Document Portal", "DocTitle"),
        p(
            "Current capabilities, student happy path, and maintenance map<br/>"
            "Prepared from the code in this workspace - 25 July 2026",
            "DocSubtitle",
        ),
    ]
    banner = Table(
        [[logo, copy]],
        colWidths=[58 * mm, 112 * mm],
        hAlign="LEFT",
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (0, 0), 8 * mm),
                ("RIGHTPADDING", (0, 0), (0, 0), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 8 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8 * mm),
                ("LEFTPADDING", (1, 0), (1, 0), 2 * mm),
                ("RIGHTPADDING", (1, 0), (1, 0), 8 * mm),
            ]
        )
    )
    return banner


def metric_table() -> Table:
    data = [
        [
            p("6", "Metric"),
            p("33", "Metric"),
            p("22", "Metric"),
            p("40 MiB", "Metric"),
        ],
        [
            p("admission phases", "MetricLabel"),
            p("document items", "MetricLabel"),
            p("student uploads", "MetricLabel"),
            p("maximum per file", "MetricLabel"),
        ],
    ]
    table = Table(data, colWidths=[42.5 * mm] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("TOPPADDING", (0, 0), (-1, 0), 4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                ("TOPPADDING", (0, 1), (-1, 1), 1 * mm),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 3 * mm),
            ]
        )
    )
    return table


def scope_band() -> Table:
    left = [
        p("What the platform is", "Subsection"),
        p(
            "A student-only Streamlit portal for viewing admission progress, "
            "opening CAS forms and templates, uploading required files, and "
            "submitting validated files through the CAS API.",
            "BodyCompact",
        ),
    ]
    right = [
        p("Deliberate scope", "Subsection"),
        p(
            "The interface offers sign in and forgot password only. It contains "
            "no registration, collaborator, or administrator workflow. The "
            "frontend holds no Dataverse or Microsoft Graph credentials.",
            "BodyCompact",
        ),
    ]
    table = Table([[left, right]], colWidths=[84 * mm, 84 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), SAGE),
                ("BACKGROUND", (1, 0), (1, 0), BLUE_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    return table


def step(number: int, title: str, body: str) -> Table:
    number_cell = Table(
        [[p(str(number), "StepNumber")]],
        colWidths=[9 * mm],
        rowHeights=[9 * mm],
    )
    number_cell.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0, GREEN),
            ]
        )
    )
    detail = [p(title, "StepTitle"), p(body, "StepBody")]
    table = Table([[number_cell, detail]], colWidths=[12 * mm, 72 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 2 * mm),
                ("RIGHTPADDING", (0, 0), (0, 0), 1 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
                ("LEFTPADDING", (1, 0), (1, 0), 1 * mm),
                ("RIGHTPADDING", (1, 0), (1, 0), 3 * mm),
            ]
        )
    )
    return table


def happy_path() -> Table:
    steps = [
        step(
            1,
            "Sign in",
            "The student enters email and password, then uses Enter or the Sign in button. "
            "A temporary <font name='Courier'>admin / admin</font> path is available for testing.",
        ),
        step(
            2,
            "Confirm the student record",
            "Real login must return <font name='Courier'>user_type=student</font> and a student ID. "
            "Admission progress is loaded and the login email is matched to the student record.",
        ),
        step(
            3,
            "Restore a secure session",
            "The portal stores a signed HMAC session cookie for up to seven days and restores the "
            "sanitized student identity on a later visit.",
        ),
        step(
            4,
            "Read the dashboard",
            "The student sees their name, email, current phase, completed upload count, percentage, "
            "and the six phase cards. Real students advance sequentially.",
        ),
        step(
            5,
            "Get the right document",
            "Buttons open external forms, global templates, or student-specific files. A missing "
            "template or individual file is shown as a disabled download action.",
        ),
        step(
            6,
            "Choose and validate files",
            "Upload controls accept PDF, JPG, JPEG, or PNG up to 40 MiB. The portal checks extension, "
            "binary signature, PDF ending, and common active-content markers.",
        ),
        step(
            7,
            "Submit and track",
            "Validated files are held as pending, submitted in one phase action through the CAS API, "
            "then reflected as saved, pending review, approved, or replacement requested.",
        ),
        step(
            8,
            "Sign out",
            "Sign out clears the in-memory student and admission progress, expires the cookie, and "
            "prevents the just-cleared cookie from being restored on the rerun.",
        ),
    ]
    rows = []
    for left_index in range(0, len(steps), 2):
        rows.append([steps[left_index], steps[left_index + 1]])
    table = Table(rows, colWidths=[84 * mm, 84 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    return table


def phase_catalog_table() -> Table:
    rows = [
        [
            p("Phase", "TableHead"),
            p("Document items defined in code", "TableHead"),
            p("Student actions", "TableHead"),
        ],
        [
            p("1. Solicitud / aplicacion", "TableCellStrong"),
            p(
                "Formulario en linea F1; Sobre mi; Entrevista; Formulario complementario F2",
                "TableCell",
            ),
            p("4 external links<br/>0 uploads", "TableCell"),
        ],
        [
            p("2. Contrato", "TableCellStrong"),
            p(
                "Contrato firmado; Condiciones generales / AGBs; Reglas del programa CAS; "
                "Factura CAS; Factura asesoria Anne; Confirmacion de admision",
                "TableCell",
            ),
            p("6 downloads<br/>5 uploads", "TableCell"),
        ],
        [
            p("3. Documentos complementarios", "TableCellStrong"),
            p(
                "Informe / recomendacion escolar; Certificado medico / de salud; Carne de "
                "vacunacion; Confirmacion de seguro en ingles; Carta a familia anfitriona; "
                "Collage de fotos; Video de presentacion; Invitacion al seminario",
                "TableCell",
            ),
            p("3 downloads<br/>7 uploads", "TableCell"),
        ],
        [
            p("4. Documentos de visa", "TableCellStrong"),
            p(
                "Partida de nacimiento con apostilla; Antecedentes penales con apostilla; Poder / "
                "autorizacion; Carta de presentacion; Formulario de visa; Escaneo de pasaporte; "
                "Escaneo del sello o adhesivo de visa; Foto tipo pasaporte",
                "TableCell",
            ),
            p("3 downloads<br/>8 uploads", "TableCell"),
        ],
        [
            p("5. Familia anfitriona y escuela", "TableCellStrong"),
            p("Perfil de familia anfitriona y escuela", "TableCell"),
            p("1 download<br/>0 uploads", "TableCell"),
        ],
        [
            p("6. Ultimas indicaciones y vuelo", "TableCellStrong"),
            p(
                "Ultimas indicaciones; Lista de equipaje; Manual CAS; E-ticket; Permiso de viaje "
                "para menores; Registro ELEFAND",
                "TableCell",
            ),
            p("6 downloads<br/>2 uploads", "TableCell"),
        ],
    ]
    table = Table(rows, colWidths=[39 * mm, 98 * mm, 31 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, SAGE]),
                ("BOX", (0, 0), (-1, -1), 0.55, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
            ]
        )
    )
    return table


def action_cards() -> Table:
    downloads = [
        p("Download behavior", "Subsection"),
        p(
            "<b>External form:</b> opens the configured URL.<br/>"
            "<b>Global template:</b> opens the API template route.<br/>"
            "<b>Student-specific file:</b> opens the document route when a document ID exists.",
            "Small",
        ),
    ]
    uploads = [
        p("Upload behavior", "Subsection"),
        p(
            "<b>Prepare:</b> validate and retain bytes, MIME type, phase, document type, and SHA-256.<br/>"
            "<b>Submit:</b> send multipart data to the student route; use the v1 fallback on HTTP 404.<br/>"
            "<b>Refresh:</b> request admission progress again after a successful response.",
            "Small",
        ),
    ]
    mobile = [
        p("Responsive behavior", "Subsection"),
        p(
            "Below 700 px, columns stack, phase actions and buttons become full width, the top submit "
            "control stays sticky, and the compact CAS header remains visible. At wider mobile sizes, "
            "the identity mark is hidden and cards reflow vertically.",
            "Small",
        ),
    ]
    table = Table([[downloads, uploads, mobile]], colWidths=[56 * mm] * 3)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), BLUE_SOFT),
                ("BACKGROUND", (1, 0), (1, 0), SAGE),
                ("BACKGROUND", (2, 0), (2, 0), GOLD_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    return table


def maintenance_table() -> Table:
    rows = [
        [
            p("Change target", "TableHead"),
            p("Primary code location", "TableHead"),
            p("Functions / structures", "TableHead"),
        ],
        [
            p("App startup and routing", "TableCellStrong"),
            p("main.py", "CodeCell"),
            p("main", "CodeCell"),
        ],
        [
            p("Sign in and password reset", "TableCellStrong"),
            p("app_pages/auth.py", "CodeCell"),
            p("_student_from_login<br/>_render_student_sign_in<br/>_render_forgot_password", "CodeCell"),
        ],
        [
            p("Signed session and sign out", "TableCellStrong"),
            p("auth/session_cookie.py", "CodeCell"),
            p("restore_auth_session<br/>start_auth_session<br/>sign_out_current_user", "CodeCell"),
        ],
        [
            p("Dashboard data load", "TableCellStrong"),
            p("app_pages/dashboard.py", "CodeCell"),
            p("_load_progress<br/>dashboard_page", "CodeCell"),
        ],
        [
            p("Phase and document contract", "TableCellStrong"),
            p("config/process.py<br/>models/file_rule.py", "CodeCell"),
            p("DEFAULT_PHASES<br/>phases_from_progress<br/>FileRule", "CodeCell"),
        ],
        [
            p("Progress and phase status", "TableCellStrong"),
            p("ui/process.py", "CodeCell"),
            p("phase_status<br/>progress_metrics<br/>render_progress_card", "CodeCell"),
        ],
        [
            p("Downloads and upload controls", "TableCellStrong"),
            p("ui/process.py", "CodeCell"),
            p("render_phase_downloads<br/>render_document_uploader<br/>render_phase_submit", "CodeCell"),
        ],
        [
            p("File acceptance and submission", "TableCellStrong"),
            p("validators/files.py<br/>document_storage.py", "CodeCell"),
            p("validate_file<br/>process_uploaded_file<br/>submit_uploaded_file<br/>prepare_document", "CodeCell"),
        ],
        [
            p("CAS API routes and transport", "TableCellStrong"),
            p("api/cas_api.py", "CodeCell"),
            p("authenticate_student<br/>get_admission_progress<br/>upload_student_file<br/>download URL helpers", "CodeCell"),
        ],
        [
            p("Responsive visual behavior", "TableCellStrong"),
            p("styles/app.py", "CodeCell"),
            p("inject_css", "CodeCell"),
        ],
        [
            p("Windows-safe local launcher", "TableCellStrong"),
            p("scripts/run_streamlit.py<br/>scripts/run_streamlit.cmd", "CodeCell"),
            p("ensure_dependencies<br/>main", "CodeCell"),
        ],
    ]
    table = Table(rows, colWidths=[46 * mm, 52 * mm, 70 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, BLUE_SOFT]),
                ("BOX", (0, 0), (-1, -1), 0.55, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
            ]
        )
    )
    return table


def readiness_table() -> Table:
    portal = [
        p("Implemented in the portal", "Subsection"),
        p(
            "Student-only forms; Enter-to-submit; temporary test login; signed session restoration; "
            "six-phase UI; progress calculation; sequential unlocking; responsive controls; file "
            "validation; multipart request construction; download URL construction; status display.",
            "Small",
        ),
    ]
    services = [
        p("Requires configured services", "Subsection"),
        p(
            "Credential validation, password-reset delivery, Dataverse-backed student and progress "
            "data, SharePoint persistence, template availability, and student-specific downloads "
            "depend on the CAS API configured by <font name='Courier'>CAS_API_BASE_URL</font>.",
            "Small",
        ),
    ]
    table = Table([[portal, services]], colWidths=[84 * mm, 84 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), SAGE),
                ("BACKGROUND", (1, 0), (1, 0), ROSE_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.6 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
            ]
        )
    )
    return table


def route_table() -> Table:
    rows = [
        [
            p("Purpose", "TableHead"),
            p("Client route", "TableHead"),
        ],
        [p("Student sign in", "TableCell"), p("POST /auth/login", "Route")],
        [p("Forgot password", "TableCell"), p("POST /auth/forgot-password", "Route")],
        [
            p("Admission progress", "TableCell"),
            p("GET /students/{student_id}/admission-progress", "Route"),
        ],
        [
            p("Student upload", "TableCell"),
            p("POST /students/{student_id}/documents/{document_type_id}/student-file", "Route"),
        ],
        [p("Upload fallback", "TableCell"), p("POST /documents/upload", "Route")],
        [p("Student-specific download", "TableCell"), p("GET /documents/{document_id}/download", "Route")],
        [
            p("Global template download", "TableCell"),
            p("GET /document-templates/{document_type_id}/download?scope=global", "Route"),
        ],
    ]
    table = Table(rows, colWidths=[48 * mm, 120 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, BLUE_SOFT]),
                ("BOX", (0, 0), (-1, -1), 0.55, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 1.6 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6 * mm),
            ]
        )
    )
    return table


def build_story() -> list:
    return [
        title_banner(),
        Spacer(1, 6 * mm),
        metric_table(),
        Spacer(1, 5 * mm),
        scope_band(),
        Spacer(1, 6 * mm),
        p("The student happy path", "Section"),
        happy_path(),
        PageBreak(),
        p("The six admission phases", "Section"),
        p(
            "The static contract is the offline fallback. When the API returns progress, the portal "
            "enriches phase status, display names, document IDs, file status, and template availability.",
            "BodyCompact",
        ),
        phase_catalog_table(),
        Spacer(1, 5 * mm),
        p("How document actions behave", "Section"),
        action_cards(),
        Spacer(1, 4 * mm),
        KeepTogether(
            [
                p("Status language shown to the student", "Subsection"),
                p(
                    "<b>Phase:</b> Pending, Ready to submit, In review, Requires attention, Waiting for "
                    "CAS, Completed, or Available. <b>File:</b> Ready to submit, Submitting, Saved to "
                    "SharePoint through the CAS API, Pending review, Approved, or Replacement requested.",
                    "Small",
                ),
            ]
        ),
        Spacer(1, 4 * mm),
        p("API routes used by the portal", "Section"),
        route_table(),
        PageBreak(),
        p("Where to change each behavior", "Section"),
        p(
            "This map keeps future edits close to the function that owns the behavior. The code already "
            "separates page flow, session handling, process configuration, file validation, API transport, "
            "and responsive styling.",
            "BodyCompact",
        ),
        maintenance_table(),
        Spacer(1, 5 * mm),
        p("Current readiness and integration boundary", "Section"),
        readiness_table(),
        Spacer(1, 4 * mm),
        p("Verification note", "Subsection"),
        p(
            "The repository test suite passed 13 tests on 25 July 2026. Coverage verifies the six-phase "
            "contract and document counts, progress enrichment, allowed file types, 40 MiB limit, binary "
            "signature checks, dangerous PDF markers, API route construction, and multipart upload content. "
            "The API calls are mocked in these tests; this is not evidence of a live Dataverse or SharePoint "
            "transaction.",
            "Small",
        ),
        Spacer(1, 2 * mm),
        p(
            "<b>Production note:</b> The <font name='Courier'>admin / admin</font> test path is intentionally "
            "temporary. The code and README both state that it must be removed before production.",
            "Small",
        ),
    ]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="CAS Student Document Portal - Current Capabilities",
        author="CAS",
        subject="Code-verified platform overview and maintenance map",
    )
    doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)
    print(OUTPUT)


if __name__ == "__main__":
    main()
