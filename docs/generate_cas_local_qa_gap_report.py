from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "CAS_local_QA_gap_report_2026-08-24.pdf"

GREEN = colors.HexColor("#145A3A")
GREEN_DARK = colors.HexColor("#0B3B27")
GREEN_LIGHT = colors.HexColor("#E8F3ED")
BLUE = colors.HexColor("#1D4ED8")
BLUE_LIGHT = colors.HexColor("#EAF0FF")
AMBER = colors.HexColor("#A16207")
AMBER_LIGHT = colors.HexColor("#FFF6DA")
RED = colors.HexColor("#B42318")
RED_LIGHT = colors.HexColor("#FDECEC")
INK = colors.HexColor("#17211B")
MUTED = colors.HexColor("#5D6A62")
LINE = colors.HexColor("#D8E2DC")
PAPER = colors.HexColor("#F7FAF8")


REGULAR, BOLD = "Helvetica", "Helvetica-Bold"
BASE = getSampleStyleSheet()
STYLES = {
    "title": ParagraphStyle(
        "Title",
        parent=BASE["Title"],
        fontName=BOLD,
        fontSize=24,
        leading=29,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=5,
    ),
    "subtitle": ParagraphStyle(
        "Subtitle",
        parent=BASE["BodyText"],
        fontName=REGULAR,
        fontSize=10.2,
        leading=14,
        textColor=colors.HexColor("#D8EEE2"),
    ),
    "h1": ParagraphStyle(
        "H1",
        parent=BASE["Heading1"],
        fontName=BOLD,
        fontSize=17,
        leading=21,
        textColor=GREEN_DARK,
        spaceBefore=4,
        spaceAfter=8,
    ),
    "h2": ParagraphStyle(
        "H2",
        parent=BASE["Heading2"],
        fontName=BOLD,
        fontSize=12,
        leading=15,
        textColor=GREEN,
        spaceBefore=8,
        spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "Body",
        parent=BASE["BodyText"],
        fontName=REGULAR,
        fontSize=9.1,
        leading=13.2,
        textColor=INK,
        spaceAfter=5,
    ),
    "small": ParagraphStyle(
        "Small",
        parent=BASE["BodyText"],
        fontName=REGULAR,
        fontSize=7.8,
        leading=10.5,
        textColor=MUTED,
    ),
    "table": ParagraphStyle(
        "Table",
        parent=BASE["BodyText"],
        fontName=REGULAR,
        fontSize=7.7,
        leading=10.2,
        textColor=INK,
    ),
    "table_bold": ParagraphStyle(
        "TableBold",
        parent=BASE["BodyText"],
        fontName=BOLD,
        fontSize=7.8,
        leading=10.3,
        textColor=INK,
    ),
    "code": ParagraphStyle(
        "Code",
        parent=BASE["Code"],
        fontName="Courier",
        fontSize=7.2,
        leading=9.7,
        textColor=GREEN_DARK,
        backColor=PAPER,
        borderColor=LINE,
        borderWidth=0.5,
        borderPadding=7,
        spaceBefore=3,
        spaceAfter=7,
    ),
    "callout": ParagraphStyle(
        "Callout",
        parent=BASE["BodyText"],
        fontName=REGULAR,
        fontSize=9,
        leading=13,
        textColor=INK,
    ),
}


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(f"<b>-</b>&nbsp; {text}", STYLES["body"])


def cell(text: str, bold: bool = False) -> Paragraph:
    return Paragraph(text, STYLES["table_bold" if bold else "table"])


def section_title(number: str, title: str) -> KeepTogether:
    return KeepTogether(
        [
            Spacer(1, 2 * mm),
            Table(
                [[p(number, "table_bold"), title]],
                colWidths=[12 * mm, 166 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, 0), GREEN),
                        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
                        ("ALIGN", (0, 0), (0, 0), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTNAME", (1, 0), (1, 0), BOLD),
                        ("FONTSIZE", (1, 0), (1, 0), 17),
                        ("LEADING", (1, 0), (1, 0), 21),
                        ("TEXTCOLOR", (1, 0), (1, 0), GREEN_DARK),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING", (1, 0), (1, 0), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                ),
            ),
        ]
    )


def callout(title: str, body: str, color: colors.Color, background: colors.Color) -> Table:
    return Table(
        [[p(title, "table_bold"), p(body, "callout")]],
        colWidths=[38 * mm, 140 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.8, color),
                ("LINEBEFORE", (0, 0), (0, 0), 4, color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        ),
    )


def data_table(rows: list[list[str]], widths: list[float], header: bool = True) -> Table:
    header_style = ParagraphStyle(
        "TableHeader",
        parent=STYLES["table_bold"],
        textColor=colors.white,
    )
    table_rows = [
        [
            Paragraph(value, header_style)
            if header and row_index == 0
            else cell(value)
            for value in row
        ]
        for row_index, row in enumerate(rows)
    ]
    style = [
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
        )
    return Table(table_rows, colWidths=widths, repeatRows=1 if header else 0, style=TableStyle(style))


class FooterCanvas(pdf_canvas.Canvas):
    def showPage(self) -> None:
        self._draw_footer()
        super().showPage()

    def _draw_footer(self) -> None:
        self.saveState()
        width, _ = A4
        self.setFillColor(MUTED)
        self.setFont(REGULAR, 7.2)
        self.drawRightString(width - 18 * mm, 9 * mm, str(self._pageNumber))
        self.restoreState()
def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=24 * mm,
        title="CAS local QA gap report",
        author="Codex",
    )
    story = []

    hero = Table(
        [[p("Revisión local de los tres repos CAS", "title")], [p("Resultado técnico, cobertura ejecutada y casos que aún requieren un buzón o cuenta controlada", "subtitle")]],
        colWidths=[178 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
                ("TOPPADDING", (0, 1), (-1, 1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 13),
            ]
        ),
    )
    story.extend([hero, Spacer(1, 7 * mm)])
    story.append(
        callout(
            "RESULTADO",
            "Los tres servicios están ejecutándose en local. CAS API se conecta correctamente a Dataverse y SharePoint; los dos portales consumen la API real y el portal colaborador ya no sustituye errores con estudiantes mock.",
            GREEN,
            GREEN_LIGHT,
        )
    )
    story.extend([Spacer(1, 5 * mm), p("Resumen verificable", "h2")])
    metrics = [
        [p("79", "h1"), p("3", "h1"), p("x2", "h1"), p("6", "h1")],
        [cell("pruebas automatizadas aprobadas"), cell("procesos locales activos"), cell("webhook idempotente ejecutado"), cell("fases cargadas desde API")],
    ]
    metric_table = Table(metrics, colWidths=[44.5 * mm] * 4)
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
            ]
        )
    )
    story.extend([metric_table, Spacer(1, 5 * mm)])
    story.append(
        data_table(
            [
                ["Servicio", "Responsabilidad final", "Local"],
                ["CAS API", "Dataverse, SharePoint, HubSpot, Resend, contraseñas, permisos y tokens", "127.0.0.1:8081"],
                ["Portal colaboradores", "Microsoft OAuth/revisor local, dashboard, revisión, invitaciones y plantillas", "localhost:8501"],
                ["Portal estudiantes", "Login, recuperación, cambio forzado, progreso, descargas y entregas", "localhost:8502"],
            ],
            [36 * mm, 104 * mm, 38 * mm],
        )
    )
    story.extend([Spacer(1, 5 * mm), p("Conclusión ejecutiva", "h2")])
    story.append(
        p(
            "La separación de responsabilidades ya es consistente con los README: los portales no guardan contraseñas, no firman identidades y no conocen credenciales de Microsoft Graph/Dataverse. El backend duplicado del portal estudiante y los flujos heredados de estudiante/correo del portal colaborador fueron eliminados."
        )
    )

    story.append(PageBreak())
    story.append(section_title("01", "Cambios aplicados"))
    story.extend(
        [
            p("CAS API", "h2"),
            bullet("Se añadieron identidades locales firmadas por la API: <b>POST /auth/local-reviewer</b> y <b>POST /auth/local-student</b>, bloqueadas fuera de <b>CAS_ENVIRONMENT=local</b>."),
            bullet("El webhook HubSpot valida firma v2, formulario permitido, email, fechas y programa; crea o actualiza el estudiante idempotentemente por correo."),
            bullet("Se centralizó el acceso temporal: hash PBKDF2, expiración, bandera de cambio obligatorio y envío por Resend, sin devolver la contraseña al frontend."),
            bullet("Se añadieron pruebas de autenticación, permisos, contraseñas temporales, invitación, webhook y subida a SharePoint simulada."),
            p("Portal colaboradores", "h2"),
            bullet("Se eliminaron registro/login/recuperación de estudiantes, envío directo por Resend y módulos duplicados de documentos."),
            bullet("Se eliminó <b>reviewer_mock.py</b>. Si la API falla, ahora se muestra un error real y un botón <b>Reintentar conexión</b>; no aparecen datos ficticios."),
            bullet("El acceso local obtiene la identidad desde CAS API y la cookie quedó aislada como <b>cas_reviewer_auth</b>."),
            bullet("Los botones de cada tipo documental respetan el contrato: revisar/aprobar/rechazar solo cuando hay entrega; descargar/subir según owner y flujo."),
            p("Portal estudiantes", "h2"),
            bullet("Se eliminó el servidor API local duplicado y sus copias de autenticación/subida. El portal contiene solo UI, validación defensiva y clientes HTTP."),
            bullet("El acceso local solicita a CAS API un token de estudiante; la cookie usa <b>cas_student_auth</b>, separada de la de revisores."),
            bullet("La contraseña temporal produce <b>password_change_required</b> y la UI cambia automáticamente a <b>Create a new password</b> antes de crear la sesión."),
            bullet("Streamlit quedó fijado en 1.60.0. Las cookies y el overlay usan la API vigente, eliminando la advertencia de <b>st.components.v1.html</b>."),
        ]
    )
    story.extend([Spacer(1, 4 * mm)])
    story.append(
        callout(
            "EXCEPCIONES",
            "Los <b>try/except</b> generales restantes están en fronteras deliberadas: servidor HTTP, llamadas de red, lotes concurrentes, health checks o limpieza de sesión. Registran el detalle en servidor y muestran mensajes seguros. Se eliminó el uso problemático: capturar un fallo de API y continuar con datos mock como si fueran reales.",
            BLUE,
            BLUE_LIGHT,
        )
    )

    story.append(PageBreak())
    story.append(section_title("02", "Casos realmente ejecutados"))
    story.append(
        data_table(
            [
                ["Caso", "Resultado", "Evidencia"],
                ["Arranque de los 3 servicios", "APROBADO", "Health de API, colaborador y estudiante = ok"],
                ["Dependencias backend", "APROBADO", "Dataverse = ok; SharePoint = ok"],
                ["Revisor local", "APROBADO", "Token emitido por API; dashboard real; logout/login repetido"],
                ["Aislamiento de sesiones", "APROBADO", "Revisor y estudiante no comparten cookie"],
                ["Invitación vacía", "APROBADO", "El botón muestra “Ingresá un correo válido” y no llama al backend"],
                ["Dashboard/revisión", "APROBADO", "22 estudiantes visibles; detalle QA; 6 fases; acciones habilitadas/deshabilitadas por estado"],
                ["Login estudiante inválido", "APROBADO", "Mensaje seguro “Invalid email or password”; sin fuga del backend"],
                ["Recuperación vacía", "APROBADO", "Validación “Enter your student email”"],
                ["Identidad estudiante local", "APROBADO", "student_id validado por API y token presente"],
                ["Webhook HubSpot local", "APROBADO", "Firma aceptada; mismo email enviado 2 veces; mismo student_id; action=updated"],
                ["Suites automatizadas", "APROBADO", "Estudiante 38; API 36; colaborador 5; total 79 (+4 subtests)"],
            ],
            [54 * mm, 24 * mm, 100 * mm],
        )
    )
    story.extend([Spacer(1, 5 * mm), p("Usuarios QA disponibles", "h2")])
    story.append(
        p(
            "Estos correos están en Dataverse y usan el dominio reservado <b>example.com</b>; sirven para filtros, HubSpot y estados documentales, pero nunca recibirán un correo real:"
        )
    )
    qa_emails = [
        "qa.hubspot.happy.20260824@example.com",
        "qa.hubspot.minimal.20260824@example.com",
        "qa.hubspot.repeat.20260824@example.com",
        "qa.hubspot.update.20260824@example.com",
        "qa.hubspot.future.20260824@example.com",
        "qa.hubspot.webhook.20260824@example.com",
    ]
    story.append(p("<br/>".join(qa_emails), "code"))
    story.append(
        callout(
            "NO ENTREGA",
            "Que el endpoint acepte estos correos no prueba Resend, recepción, spam, enlace ni experiencia de bandeja. Para eso hace falta un buzón QA controlado y autorizado.",
            AMBER,
            AMBER_LIGHT,
        )
    )

    story.append(PageBreak())
    story.append(section_title("03", "Casos no probados y por qué"))
    story.append(
        data_table(
            [
                ["Prioridad", "Caso pendiente", "Motivo / qué falta"],
                ["P0", "Invitación con correo real", "Falta confirmar un buzón QA exacto. El envío crea/actualiza acceso y representa a CAS ante un destinatario."],
                ["P0", "Recibir y usar contraseña temporal", "Los example.com no entregan. Hace falta abrir el correo en un buzón controlado y copiar la contraseña temporal."],
                ["P0", "Cambio final de contraseña en navegador", "La redirección automática está cubierta por código y pruebas; falta el secreto temporal real. El clic final debe hacerlo el dueño del buzón."],
                ["P0", "Recuperación desde buzón", "Backend y validación están cubiertos, pero no la entrega de Resend ni el uso completo del mensaje."],
                ["P1", "OAuth Microsoft @cas.cr", "Requiere una cuenta CAS interactiva, MFA y redirect URI configurado; no se usaron credenciales personales."],
                ["P1", "Webhook desde HubSpot público", "Se probó el mismo formato y firma en local; falta desplegar HTTPS y ejecutar el workflow real de cada formulario."],
                ["P1", "Aprobar/rechazar documento real", "Los botones y API están cubiertos, pero no se cambió el estado de un documento compartido sin designar un registro QA descartable."],
                ["P1", "Subir/descargar en SharePoint", "Conectividad y rutas están sanas; no se escribió ni descargó un archivo real sin acordar el documento QA y el archivo de prueba."],
                ["P2", "Entregabilidad/antispam", "Requiere dominio Resend verificado, DNS, mailbox real y revisión de spam/rebotes."],
                ["P2", "Carga y concurrencia", "No se ejecutó una prueba sostenida con múltiples revisores/estudiantes o archivos grandes."],
            ],
            [18 * mm, 58 * mm, 102 * mm],
        )
    )
    story.extend([Spacer(1, 5 * mm)])
    story.append(
        callout(
            "DECISIÓN DE PRODUCTO",
            "El flujo implementado de “olvidé mi contraseña” envía una <b>contraseña temporal</b>, no un código numérico. Si el requisito final es recibir e ingresar un código OTP, ese caso de uso no existe hoy y requiere un diseño distinto de tabla/token, expiración, reintentos y pantalla.",
            RED,
            RED_LIGHT,
        )
    )
    story.extend([Spacer(1, 5 * mm), p("Orden recomendado para cerrar P0", "h2")])
    for item in [
        "Confirmar por escrito un buzón QA (por ejemplo, un alias dedicado) y no reutilizar un correo personal sin permiso.",
        "Crear/actualizar ese estudiante mediante un formulario HubSpot QA o el webhook local con <b>--allow-non-example-email</b>.",
        "Desde el portal colaborador, pulsar <b>Invitar estudiante</b> una sola vez y comprobar recepción/remitente/contenido.",
        "Ingresar la contraseña temporal en el portal estudiante; verificar que aparece automáticamente <b>Create a new password</b>.",
        "El dueño del buzón completa el cambio final, cierra sesión, vuelve a entrar y luego prueba <b>Forgot password?</b>.",
    ]:
        story.append(bullet(item))

    story.append(PageBreak())
    story.append(section_title("04", "Cómo repetir la prueba desde cero"))
    story.append(p("Terminal 1 · CAS API", "h2"))
    story.append(
        p(
            "cd ..\\cas-api<br/>"
            "# cargar .env.api.local sin imprimir secretos<br/>"
            "python -m cas_api.server",
            "code",
        )
    )
    story.append(p("Terminal 2 · Portal colaboradores", "h2"))
    story.append(
        p(
            "cd cas-collaborator-platform<br/>"
            "python -m streamlit run main_colaboradores.py --server.port 8501 --server.address 127.0.0.1",
            "code",
        )
    )
    story.append(p("Terminal 3 · Portal estudiantes", "h2"))
    story.append(p("cd Streamlit-inventory-dashboard<br/>.\\scripts\\run_streamlit.cmd --port 8502", "code"))
    story.append(p("Crear/refrescar datos QA", "h2"))
    story.append(
        p(
            "# vista previa, sin escritura<br/>"
            "python scripts/seed_hubspot_qa_users.py<br/><br/>"
            "# estudiantes QA<br/>"
            "python scripts/seed_hubspot_qa_users.py --apply<br/><br/>"
            "# añade estados documentales mock claramente marcados<br/>"
            "python scripts/seed_hubspot_qa_users.py --apply --documents",
            "code",
        )
    )
    story.append(p("Pruebas y smoke test", "h2"))
    story.append(
        p(
            "python -m pytest -q<br/>"
            "python scripts/smoke_test_local_stack.py<br/>"
            "python scripts/send_test_hubspot_webhook.py<br/>"
            "python scripts/send_test_hubspot_webhook.py --send",
            "code",
        )
    )
    story.append(
        callout(
            "REGLA DE SEGURIDAD",
            "El seeder solo modifica IDs con prefijo <b>QA-HUBSPOT-20260824-</b> y documentos mock reconocibles. Usar primero el modo vista previa. No copiar secretos a los portales ni al navegador.",
            GREEN,
            GREEN_LIGHT,
        )
    )
    story.extend([Spacer(1, 5 * mm), p("Criterio de cierre", "h2")])
    story.append(
        p(
            "El flujo podrá considerarse probado de punta a punta cuando un único buzón QA complete: HubSpot &gt; Dataverse &gt; invitación Resend &gt; login temporal &gt; redirección automática &gt; cambio de contraseña &gt; login normal &gt; recuperación; y cuando un registro documental QA complete subida &gt; revisión &gt; rechazo &gt; reemplazo &gt; aprobación sin tocar datos productivos."
        )
    )

    doc.build(story, canvasmaker=FooterCanvas)
    print(OUTPUT)


if __name__ == "__main__":
    build()
