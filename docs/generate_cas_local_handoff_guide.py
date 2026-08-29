from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "CAS_local_environment_handoff_for_Codex_2026-08-28.pdf"

NAVY = colors.HexColor("#0A2333")
GREEN = colors.HexColor("#1B5936")
MINT = colors.HexColor("#E7F3E7")
CREAM = colors.HexColor("#F7F3EA")
GOLD = colors.HexColor("#C89B3C")
RED = colors.HexColor("#A33A35")
AMBER = colors.HexColor("#9A6500")
GRAY = colors.HexColor("#5B6870")
LIGHT_GRAY = colors.HexColor("#D7DFE0")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("CAS", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("CAS-Bold", r"C:\Windows\Fonts\arialbd.ttf"))


def build_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=sample["Title"],
            fontName="CAS-Bold",
            fontSize=29,
            leading=34,
            textColor=WHITE,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=sample["Normal"],
            fontName="CAS",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#DDE9E3"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=sample["Heading1"],
            fontName="CAS-Bold",
            fontSize=19,
            leading=23,
            textColor=NAVY,
            spaceBefore=3,
            spaceAfter=10,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=sample["Heading2"],
            fontName="CAS-Bold",
            fontSize=13.5,
            leading=17,
            textColor=GREEN,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=sample["Heading3"],
            fontName="CAS-Bold",
            fontSize=10.5,
            leading=14,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="CAS",
            fontSize=9.2,
            leading=13,
            textColor=colors.HexColor("#24343D"),
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["BodyText"],
            fontName="CAS",
            fontSize=7.3,
            leading=9.7,
            textColor=colors.HexColor("#34444D"),
        ),
        "small_bold": ParagraphStyle(
            "SmallBold",
            parent=sample["BodyText"],
            fontName="CAS-Bold",
            fontSize=7.3,
            leading=9.7,
            textColor=WHITE,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="CAS",
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#24343D"),
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=3,
        ),
        "bullet_child": ParagraphStyle(
            "BulletChild",
            parent=sample["BodyText"],
            fontName="CAS",
            fontSize=8.6,
            leading=12,
            textColor=colors.HexColor("#34444D"),
            leftIndent=29,
            firstLineIndent=-10,
            spaceAfter=2.5,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=sample["Code"],
            fontName="Courier",
            fontSize=7.1,
            leading=9.7,
            textColor=NAVY,
            backColor=colors.HexColor("#EDF1F2"),
            borderColor=LIGHT_GRAY,
            borderWidth=0.5,
            borderPadding=6,
            spaceBefore=3,
            spaceAfter=7,
        ),
        "callout_title": ParagraphStyle(
            "CalloutTitle",
            parent=sample["BodyText"],
            fontName="CAS-Bold",
            fontSize=9.2,
            leading=12.5,
            textColor=NAVY,
        ),
    }


S: dict[str, ParagraphStyle]


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def heading(text: str, level: int = 1) -> Paragraph:
    return Paragraph(text, S[f"h{level}"])


def bullet(text: str, child: bool = False) -> Paragraph:
    return Paragraph(f"- {text}", S["bullet_child" if child else "bullet"])


def code(text: str) -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>"), S["code"])


def callout(title: str, text: str, tone: str = "green") -> Table:
    palette = {
        "green": (GREEN, MINT),
        "amber": (AMBER, colors.HexColor("#FFF4D6")),
        "red": (RED, colors.HexColor("#FCE8E6")),
        "navy": (NAVY, colors.HexColor("#E9F0F4")),
    }
    accent, fill = palette[tone]
    table = Table(
        [[Paragraph(title, S["callout_title"]), p(text)]],
        colWidths=[34 * mm, 132 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
                ("BOX", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def table(headers: list[str], rows: list[list[str]], widths: list[float]) -> LongTable:
    data = [[Paragraph(esc(value), S["small_bold"]) for value in headers]]
    for row in rows:
        data.append([Paragraph(esc(value).replace("\n", "<br/>"), S["small"]) for value in row])
    result = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD4D7")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F3F6F5")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return result


def page_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    if doc.page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
    else:
        canvas.setFillColor(CREAM)
        canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
        canvas.setFillColor(GREEN)
        canvas.setFont("CAS-Bold", 8)
        canvas.drawString(20 * mm, height - 9.5 * mm, "CAS LOCAL ENVIRONMENT HANDOFF")
        canvas.setFillColor(GRAY)
        canvas.setFont("CAS", 7.5)
        canvas.drawRightString(width - 20 * mm, height - 9.5 * mm, "Codex-ready setup guide")
        canvas.setStrokeColor(LIGHT_GRAY)
        canvas.line(20 * mm, 14 * mm, width - 20 * mm, 14 * mm)
        canvas.drawString(20 * mm, 9 * mm, "Prepared 28 August 2026 - No live credentials included")
        canvas.drawRightString(width - 20 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def add_section(story: list, title: str, intro: str | None = None, new_page: bool = False) -> None:
    if new_page:
        story.append(PageBreak())
    story.append(heading(title))
    if intro:
        story.append(p(intro))


def build_story() -> list:
    story: list = []

    story.extend(
        [
            Spacer(1, 23 * mm),
            p("CAS", "cover_subtitle"),
            Spacer(1, 18 * mm),
            Paragraph("Local environment handoff", S["cover_title"]),
            Paragraph(
                "API, Student Portal and Collaborator Portal - structured for a Codex-assisted setup",
                S["cover_subtitle"],
            ),
            Spacer(1, 15 * mm),
        ]
    )
    cover_table = Table(
        [
            [p("1. Clone", "callout_title"), p("Three GitHub repositories in the expected workspace layout")],
            [p("2. Configure", "callout_title"), p("Create ignored local environment files from committed examples")],
            [p("3. Run", "callout_title"), p("One command per service, or one Docker stack command")],
            [p("4. Verify", "callout_title"), p("Health endpoints, sign-in, invitation, recovery and document flows")],
        ],
        colWidths=[34 * mm, 132 * mm],
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7F3E7")),
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#9AB3A7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend(
        [
            cover_table,
            Spacer(1, 15 * mm),
            Paragraph(
                "Safe to share as project documentation. Secret values must be transferred separately through an approved password manager or secure channel.",
                S["cover_subtitle"],
            ),
            Spacer(1, 23 * mm),
            Paragraph("Repository state: main - 28 August 2026", S["cover_subtitle"]),
        ]
    )

    add_section(story, "1. What to share", new_page=True)
    story.extend(
        [
            callout(
                "Security boundary",
                "This PDF contains environment-variable names and placeholders only. Do not place real client secrets, API tokens, Resend keys, or cookie secrets in Git, email, chat, screenshots, or a Codex prompt.",
                "red",
            ),
            Spacer(1, 5 * mm),
            bullet("Grant your teammate access to all three GitHub repositories."),
            bullet("Share this PDF so Codex can follow the exact layout and commands."),
            bullet("Transfer only the required secret values through a password manager or another approved secure channel."),
            bullet("Tell your teammate which Microsoft account can sign in and which non-production mailbox can receive Resend email."),
            bullet("Do not share any existing .env.*.local file. Each developer creates their own ignored copy."),
            heading("Pinned repository state", 2),
            table(
                ["Component", "GitHub repository", "Commit on main"],
                [
                    ["CAS API", "https://github.com/djwhitee/cas-api.git", "05cd4395cd4f"],
                    ["Student Portal", "https://github.com/joseSalazar4/Streamlit-inventory-dashboard.git", "a08ef1dee5fe"],
                    ["Collaborator Portal", "https://github.com/djwhitee/cas-document-platform.git", "f934b63e8b1e"],
                ],
                [31 * mm, 99 * mm, 36 * mm],
            ),
        ]
    )

    add_section(story, "2. Expected Windows workspace layout", new_page=True)
    story.extend(
        [
            p(
                "The shared Docker launcher expects the collaborator repository inside the student repository's ignored .local directory. The individual launchers also work independently."
            ),
            code(
                "C:\\Users\\<USER>\\Desktop\\CAS Code\\\n"
                "  cas-api\\\n"
                "  Streamlit-inventory-dashboard\\\n"
                "    .local\\\n"
                "      cas-document-platform\\\n"
                "        cas-collaborator-platform\\"
            ),
            heading("Clone commands", 2),
            code(
                "New-Item -ItemType Directory -Force \"$HOME\\Desktop\\CAS Code\" | Out-Null\n"
                "cd \"$HOME\\Desktop\\CAS Code\"\n\n"
                "git clone https://github.com/djwhitee/cas-api.git\n"
                "git clone https://github.com/joseSalazar4/Streamlit-inventory-dashboard.git\n\n"
                "New-Item -ItemType Directory -Force \".\\Streamlit-inventory-dashboard\\.local\" | Out-Null\n"
                "git clone https://github.com/djwhitee/cas-document-platform.git "
                "\".\\Streamlit-inventory-dashboard\\.local\\cas-document-platform\""
            ),
            callout(
                "Private repositories",
                "If Git prompts for access, sign in through Git Credential Manager or authorize the GitHub account first. Codex should not be given a personal access token in a prompt.",
                "amber",
            ),
        ]
    )

    add_section(story, "3. Environment files", new_page=True)
    story.extend(
        [
            p(
                "Local launchers load ignored .env files automatically. Azure Container Apps will use runtime environment variables and Key Vault references instead. The committed .example files are the source of truth for names."
            ),
            table(
                ["Service", "Committed template", "Ignored local file", "Creation"],
                [
                    ["API", ".env.api.example", ".env.api.local", "Copy once and fill placeholders"],
                    ["Students", ".env.streamlit.example", ".env.streamlit.local", "Copy once and fill placeholders"],
                    ["Collaborators", "cas-collaborator-platform/.env.example", "cas-collaborator-platform/.env.local", "Generated by first .\\run-local.cmd when API env exists"],
                ],
                [29 * mm, 42 * mm, 47 * mm, 48 * mm],
            ),
            heading("Create the API and student files", 2),
            code(
                "cd \"$HOME\\Desktop\\CAS Code\\cas-api\"\n"
                "Copy-Item .env.api.example .env.api.local\n\n"
                "cd \"$HOME\\Desktop\\CAS Code\\Streamlit-inventory-dashboard\"\n"
                "Copy-Item .env.streamlit.example .env.streamlit.local"
            ),
            callout(
                "One-time input",
                "A configuration format cannot remove the need to provide credentials. The simplification is that credentials are entered once, ignored by Git, then loaded automatically on every run.",
                "navy",
            ),
        ]
    )

    add_section(story, "4. CAS API environment keys", new_page=True)
    api_rows = [
        ["CAS_ENVIRONMENT", "Config", "local", "Required"],
        ["CAS_API_HOST", "Config", "127.0.0.1 locally; 0.0.0.0 in container", "Required"],
        ["CAS_API_PORT", "Config", "8081 locally; 8080 in container", "Required"],
        ["CAS_API_TIMING", "Config", "1 for local diagnostics", "Optional"],
        ["CAS_API_REQUIRE_AUTH", "Security", "1", "Required"],
        ["CAS_API_AUTH_TOKEN", "Secret", "Long random token; exact same value in both portals", "Required"],
        ["CAS_API_USER_TOKEN_SECRET", "Secret", "Different long random signing value", "Required"],
        ["CAS_API_DATAVERSE_TENANT_ID", "Identifier", "Microsoft tenant that owns Dataverse", "Required"],
        ["CAS_API_DATAVERSE_CLIENT_ID", "Identifier", "Dataverse app registration client ID", "Required"],
        ["CAS_API_DATAVERSE_CLIENT_SECRET", "Secret", "Dataverse app registration secret", "Required"],
        ["CAS_API_DATAVERSE_URL", "URL", "https://<org>.crm.dynamics.com", "Required"],
        ["CAS_API_SHAREPOINT_TENANT_ID", "Identifier", "CAS Microsoft tenant", "Required"],
        ["CAS_API_SHAREPOINT_CLIENT_ID", "Identifier", "SharePoint app registration client ID", "Required"],
        ["CAS_API_SHAREPOINT_CLIENT_SECRET", "Secret", "SharePoint app registration secret", "Required"],
        ["CAS_API_SHAREPOINT_HOSTNAME", "Host", "<tenant>.sharepoint.com", "Required"],
        ["CAS_API_SHAREPOINT_SITE_PATH", "Path", "/sites/<site>", "Required"],
        ["CAS_API_SHAREPOINT_BASE_FOLDER", "Path", "CAS Drive/OPTIMA/Plataforma Documentos", "Required"],
        ["CAS_API_PASSWORD_RESET_SECRET", "Secret", "Long random password-flow signing value", "Required for email flows"],
        ["RESEND_API_KEY", "Secret", "Sending-only key for verified domain", "Required for email flows"],
        ["RESEND_FROM_EMAIL", "Email", "Verified CAS sender identity", "Required for email flows"],
        ["CAS_PORTAL_URL", "URL", "http://localhost:8502 locally", "Required for email links"],
        ["CAS_HUBSPOT_CLIENT_SECRET", "Secret", "HubSpot workflow signature secret", "Required for webhook"],
        ["CAS_HUBSPOT_ALLOWED_FORM_IDS", "Config", "Comma-separated allowed form IDs", "Required for webhook"],
        ["CAS_HUBSPOT_WEBHOOK_PUBLIC_URL", "URL", "Public HTTPS webhook URL", "Required for HubSpot"],
    ]
    story.extend(
        [
            p("File: cas-api/.env.api.local. Start from cas-api/.env.api.example."),
            table(
                ["Key", "Type", "Expected source or value", "Use"],
                api_rows,
                [49 * mm, 21 * mm, 70 * mm, 26 * mm],
            ),
            heading("Optional advanced API keys", 2),
            bullet("CAS_API_DATAVERSE_LABEL_LANGUAGE_CODE - Dataverse localized label language."),
            bullet("CAS_AUTOMATCHING_API_ENABLED - enables automatching API routes."),
            bullet("CAS_AUTOMATCHING_ENGINE_MODE - selects the configured matching engine mode."),
            bullet("CAS_AUTOMATCHING_WRITE_ENABLED - permits automatching writes; keep disabled until explicitly tested."),
            bullet("CAS_RATE_LIMIT_DISABLED - local diagnostics only; never disable production rate limiting."),
        ]
    )

    add_section(story, "5. Student and collaborator portal keys", new_page=True)
    story.extend(
        [
            heading("Student Portal - .env.streamlit.local", 2),
            table(
                ["Key", "Type", "Expected source or value", "Use"],
                [
                    ["CAS_ENVIRONMENT", "Config", "local", "Required"],
                    ["CAS_API_BASE_URL", "URL", "http://127.0.0.1:8081", "Required"],
                    ["CAS_API_AUTH_TOKEN", "Secret", "Must exactly match API token", "Required"],
                    ["AUTH_COOKIE_SECRET", "Secret", "Unique long random value for student sessions", "Required"],
                    ["CAS_TEST_STUDENT_ID", "Identifier", "Non-production Dataverse student ID", "Optional local shortcut"],
                    ["CAS_TEST_STUDENT_NAME", "Display", "Friendly QA name", "Optional local shortcut"],
                ],
                [49 * mm, 22 * mm, 69 * mm, 26 * mm],
            ),
            heading("Collaborator Portal - .env.local", 2),
            table(
                ["Key", "Type", "Expected source or value", "Use"],
                [
                    ["CAS_ENVIRONMENT", "Config", "local", "Required"],
                    ["CAS_API_BASE_URL", "URL", "http://127.0.0.1:8081", "Required"],
                    ["CAS_API_AUTH_TOKEN", "Secret", "Must exactly match API token", "Required"],
                    ["AUTH_COOKIE_SECRET", "Secret", "Unique long random value for collaborator sessions", "Required"],
                    ["CAS_MICROSOFT_TENANT_ID", "Identifier", "CAS tenant ID", "Required"],
                    ["CAS_MICROSOFT_CLIENT_ID", "Identifier", "Web app registration client ID", "Required"],
                    ["CAS_MICROSOFT_CLIENT_SECRET", "Secret", "Web app registration secret", "Required"],
                    ["CAS_MICROSOFT_REDIRECT_URI", "URL", "http://localhost:8501", "Required"],
                    ["CAS_STREAMLIT_TIMING", "Config", "1 for local diagnostics", "Optional"],
                ],
                [49 * mm, 22 * mm, 69 * mm, 26 * mm],
            ),
            callout(
                "Automatic collaborator setup",
                "On first run, the collaborator launcher finds cas-api/.env.api.local, copies only the API token and the SharePoint app values needed for Microsoft OAuth, generates a separate cookie secret, and writes an ignored .env.local. Delete that file to regenerate it after local credential rotation.",
                "green",
            ),
        ]
    )

    add_section(story, "6. Start the platform", new_page=True)
    story.extend(
        [
            p("Open three PowerShell terminals. Run one block in each terminal."),
            heading("Terminal 1 - API", 2),
            code(
                "cd \"$HOME\\Desktop\\CAS Code\\cas-api\"\n"
                ".\\run-local.cmd"
            ),
            heading("Terminal 2 - Collaborators", 2),
            code(
                "cd \"$HOME\\Desktop\\CAS Code\\Streamlit-inventory-dashboard\\.local\\cas-document-platform\\cas-collaborator-platform\"\n"
                ".\\run-local.cmd"
            ),
            heading("Terminal 3 - Students", 2),
            code(
                "cd \"$HOME\\Desktop\\CAS Code\\Streamlit-inventory-dashboard\"\n"
                ".\\run-local.cmd"
            ),
            heading("Expected endpoints", 2),
            table(
                ["Service", "URL", "Health check"],
                [
                    ["API", "http://127.0.0.1:8081", "http://127.0.0.1:8081/health"],
                    ["Collaborators", "http://localhost:8501", "http://127.0.0.1:8501/_stcore/health"],
                    ["Students", "http://127.0.0.1:8502", "http://127.0.0.1:8502/_stcore/health"],
                ],
                [36 * mm, 61 * mm, 69 * mm],
            ),
            heading("PowerShell health verification", 2),
            code(
                "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8081/health\n"
                "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8501/_stcore/health\n"
                "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8502/_stcore/health"
            ),
            p("Stop any service with Ctrl+C in its terminal."),
        ]
    )

    add_section(story, "7. Docker workflow", new_page=True)
    story.extend(
        [
            p(
                "Docker is optional for individual local development but recommended for production parity. Docker Desktop must be installed and running."
            ),
            code(
                "cd \"$HOME\\Desktop\\CAS Code\\Streamlit-inventory-dashboard\"\n"
                ".\\run-local-stack.cmd"
            ),
            p("The command prepares the collaborator environment, builds all three images, then starts:"),
            bullet("API container: host port 8081 to container port 8080."),
            bullet("Collaborator container: host port 8501 to container port 8501."),
            bullet("Student container: host port 8502 to container port 8501."),
            code("docker compose down"),
            callout(
                "Image rule",
                "Never bake .env files or secrets into an image. The committed .dockerignore files exclude local environment files. Build one immutable image per repository and inject configuration when the container starts.",
                "red",
            ),
        ]
    )

    add_section(story, "8. Azure mapping", new_page=True)
    story.extend(
        [
            p(
                "For Azure Container Apps, do not upload the local .env files. Create application secrets or Key Vault references, then map them to environment variables with the exact names below."
            ),
            table(
                ["Container App", "Normal environment variables", "Secrets / Key Vault references"],
                [
                    [
                        "CAS API",
                        "CAS_ENVIRONMENT, CAS_API_HOST, CAS_API_PORT, Dataverse URL, SharePoint hostname/site/folder, CAS_PORTAL_URL, HubSpot allowed IDs/public URL",
                        "API auth token, user-token secret, Dataverse client secret, SharePoint client secret, password-reset secret, Resend key, HubSpot secret",
                    ],
                    [
                        "Students",
                        "CAS_ENVIRONMENT, CAS_API_BASE_URL",
                        "CAS_API_AUTH_TOKEN, AUTH_COOKIE_SECRET",
                    ],
                    [
                        "Collaborators",
                        "CAS_ENVIRONMENT, CAS_API_BASE_URL, Microsoft tenant/client IDs, production redirect URI",
                        "CAS_API_AUTH_TOKEN, AUTH_COOKIE_SECRET, CAS_MICROSOFT_CLIENT_SECRET",
                    ],
                ],
                [33 * mm, 66 * mm, 67 * mm],
            ),
            bullet("Use the Azure API hostname for both portal CAS_API_BASE_URL values."),
            bullet("Set CAS_PORTAL_URL to the public Student Portal HTTPS hostname."),
            bullet("Add the exact production Collaborator Portal callback URL to the Entra app registration."),
            bullet("Set the public API webhook URL in HubSpot and verify its request signature."),
            bullet("Deploy commit-specific image tags. Do not depend only on latest."),
        ]
    )

    add_section(story, "9. Codex setup prompt", new_page=True)
    story.extend(
        [
            p("Paste the following prompt into Codex after sharing repository access and this PDF:"),
            code(
                "Set up the CAS platform locally on Windows from the three repositories documented in this PDF.\n\n"
                "Constraints:\n"
                "- Never print, log, commit, or repeat secret values.\n"
                "- Do not invent missing credentials. Ask me for the specific missing key name only.\n"
                "- Preserve the documented folder layout because compose.yaml references it.\n"
                "- Use the committed .example files as the configuration contract.\n"
                "- Keep every .env.*.local file ignored by Git.\n"
                "- Do not modify production Azure resources.\n\n"
                "Tasks:\n"
                "1. Clone or update all three main branches.\n"
                "2. Confirm the pinned commits or newer main commits.\n"
                "3. Create missing API and student local env files from their examples.\n"
                "4. Ask me securely for only the missing secret values.\n"
                "5. Run each .\\run-local.cmd launcher.\n"
                "6. Verify API 8081, collaborators 8501, and students 8502 health endpoints.\n"
                "7. Test Microsoft collaborator sign-in and student login without mock fallbacks.\n"
                "8. Report failures using key names and safe summaries, never credential values."
            ),
            callout(
                "Codex handoff",
                "Codex can create files and run validation, but the human owner must provide secrets and approve any external or production mutation."
                ,
                "navy",
            ),
        ]
    )

    add_section(story, "10. Troubleshooting and acceptance checklist", new_page=True)
    story.extend(
        [
            heading("Common setup failures", 2),
            bullet("Python not found: install Python 3.10+ or set CAS_PYTHON_EXE to a valid python.exe. The launchers also detect the Codex bundled runtime."),
            bullet("Port already in use: stop the previous process or inspect it with Get-NetTCPConnection -State Listen -LocalPort 8081,8501,8502."),
            bullet("API returns 401: confirm both portal CAS_API_AUTH_TOKEN values exactly match the API value."),
            bullet("Microsoft redirect error: confirm http://localhost:8501 is registered as a Web redirect URI for local use."),
            bullet("Resend email fails: confirm the API key is active and RESEND_FROM_EMAIL belongs to a verified sending domain."),
            bullet("HubSpot cannot reach localhost: use an approved public HTTPS tunnel for local webhook tests or deploy the API first."),
            bullet("Collaborator config is stale: delete its ignored .env.local and rerun .\\run-local.cmd to regenerate it."),
            heading("Acceptance checklist", 2),
        ]
    )
    for item in [
        "[ ] All three repositories are on main and have no unexpected local changes.",
        "[ ] No .env local file or secrets.toml file is tracked by Git.",
        "[ ] API /health returns HTTP 200.",
        "[ ] Both Streamlit health endpoints return HTTP 200.",
        "[ ] A valid @cas.cr collaborator completes Microsoft OAuth.",
        "[ ] The collaborator portal reads real API data and never shows mock fallback records.",
        "[ ] A controlled test student receives an invitation email.",
        "[ ] Temporary-password login forces the new-password screen.",
        "[ ] Forgot-password email works and the new temporary password forces a change.",
        "[ ] Student upload, collaborator review, rejection comment and replacement flows are verified.",
        "[ ] HubSpot webhook rejects invalid signatures and processes an allowed form idempotently.",
        "[ ] No browser or API error reveals credentials or raw internal exceptions.",
    ]:
        story.append(bullet(item))

    story.extend(
        [
            Spacer(1, 4 * mm),
            callout(
                "Ready for deployment",
                "After this checklist passes, create Azure Container Registry and the three Container Apps, configure Key Vault-backed secrets, then add CI/CD so each push to main builds and deploys its repository image automatically.",
                "green",
            ),
        ]
    )
    return story


def main() -> None:
    global S
    register_fonts()
    S = build_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="CAS Local Environment Handoff for Codex",
        author="CAS platform project",
        subject="Safe local configuration and startup guide for the CAS API and portals",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="CAS", frames=[frame], onPage=page_header_footer)])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
