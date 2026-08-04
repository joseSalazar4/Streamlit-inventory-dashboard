# CAS student document portal

Streamlit portal for CAS students to follow the six-phase admission process,
download CAS templates, and submit files through the CAS API.

## Run locally

Use the pinned Streamlit version from `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit version
```

The expected Streamlit version is `1.50.0`. Do not rely on a globally installed
Streamlit from another project; small API differences can break widgets.

Windows App Control may block the generated `streamlit.exe` launcher. Use the
repository launcher instead:

```powershell
.\scripts\run_cas_api.cmd
```

In a second terminal:

```powershell
.\scripts\run_streamlit.cmd
```

To use another port:

```powershell
.\scripts\run_streamlit.cmd --port 8514
```

The app binds to all local network interfaces. From a phone on the same Wi-Fi,
open `http://<computer-ip>:8501`. Find the computer's IPv4 address with
`ipconfig`. If the local URL works but the phone cannot connect, allow the
bundled Python process or the selected TCP port through Windows Firewall on
Private networks.

Local values are loaded from two files that are ignored by Git:

```text
.env.api.local
.env.streamlit.local
```

Use `.env.api.example` and `.env.streamlit.example` as the safe templates.
The student portal only needs `CAS_API_BASE_URL` and `AUTH_COOKIE_SECRET`.
Microsoft OAuth variables belong to the collaborator portal and are not loaded.

## Authentication

The portal has student sign-in, forgot-password, and forced password-change
flows. It does not provide account registration or a collaborator/admin
interface.

Real student login calls:

```text
POST /auth/login
POST /auth/change-password
GET  /students/{student_id}/admission-progress
```

The API login response must identify `user_type=student` and include a
`student_id`. The progress lookup confirms that the account maps to a Dataverse
student and supplies the student's display name and current phase.

Temporary local test access is enabled only when `CAS_TEST_STUDENT_ID` is set:

```text
username: admin
password: admin
```

Use only a non-production test student ID. Leave `CAS_TEST_STUDENT_ID` unset in
production; the `admin/admin` shortcut is disabled by default.

## CAS API

The local Streamlit environment points to `CAS_API_BASE_URL`. In the current
local setup this is usually `http://127.0.0.1:8080`; use `8081` only when
running a temporary API instance.

The Streamlit portal never receives Dataverse or Microsoft Graph credentials.
It targets the routes in the `djwhitee/cas-document-platform` API contract:

```text
POST /auth/login
POST /auth/forgot-password
POST /auth/change-password
GET  /students/{student_id}/admission-progress
POST /students/{student_id}/documents/{document_type_id}/student-file
POST /documents/upload
GET  /documents/{document_id}/download
GET  /document-templates/{document_type_id}/download?scope=global
```

At upstream commit `b11c2dc`, `cas-api/cas_api/server.py` does not yet register
the student authentication, password reset, or student-upload routes. The local
`run_cas_api` launcher extends that server with these routes.

Password reset uses `opti_portal_users.opti_password_hash`. Only a salted
PBKDF2 hash is stored. A temporary-password marker and expiry are encoded in
that hash, so no plaintext password or additional reset table is required.
Successful temporary-password login returns a short-lived signed authorization
for one forced password change. If an exact student email exists but has no
portal-user row yet, the first reset request creates and links that student
portal account.

Configure email delivery in `.env.api.local`:

```text
CAS_API_PASSWORD_RESET_SECRET=<long random server-side secret>
RESEND_API_KEY=re_xxxxxxxxx
RESEND_FROM_EMAIL=CAS Document Portal <noreply@updates.yourdomain.com>
CAS_PORTAL_URL=https://portal.yourdomain.com
```

The sending address must use a domain verified in Resend. The reset endpoint
stays unavailable until all four settings are present, preventing a password
from being replaced when no email can be delivered.

Student uploads use the student-specific route first and fall back to the
resource-oriented `/documents/upload` route for API contract compatibility.
When a phase contains multiple ready files, Streamlit sends one concurrent
request per file. The API server handles those requests in separate threads,
then the UI refreshes admission progress once after the batch finishes.
The API owns the SharePoint path and version:

```text
CAS Drive/OPTIMA/Plataforma Documentos/
  Admissions/{student_id}/{document_type_id}/{version}/{file_name}
```

Global templates are resolved by the API from:

```text
Templates/global/{document_type_id}/{version}/{file_name}
```

## Admission phases

The UI mirrors the collaborator repository's current admission contract:

1. Solicitud / aplicacion
2. Contrato
3. Documentos complementarios
4. Documentos de visa
5. Familia anfitriona y escuela
6. Ultimas indicaciones y vuelo

The static definitions in `config/process.py` are the offline fallback. When
Dataverse progress is available, document IDs, statuses, display names, and
download availability are enriched from the API response.

## File security

Student upload widgets accept only:

```text
pdf, jpg, jpeg, png
```

The maximum file size is 40 MiB. Validation checks the extension, size, and
binary structure before the file can be submitted. PDFs with common active
content markers such as scripts, embedded files, launch actions, or automatic
open actions are rejected. The CAS API must repeat validation and malware
scanning because frontend checks are defense in depth, not the security boundary.
