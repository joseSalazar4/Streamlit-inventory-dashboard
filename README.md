# CAS student document portal

Streamlit portal for CAS students to follow the six-phase admission process,
download CAS templates, and submit files through the CAS API.

## General platform use cases

The complete local platform consists of three applications. Each application
has a single responsibility and communicates with the others only through the
CAS API contract.

| Component | Main actor | Responsibility |
| --- | --- | --- |
| CAS API (`cas-api`, port `8081`) | System | Owns authentication, permissions, HubSpot intake, Dataverse, SharePoint, password state, signed tokens, and email delivery through Resend. |
| Collaborator portal (`cas-collaborator-platform`, port `8501`) | CAS reviewer or administrator | Searches students, creates portal access, reviews documents, uploads CAS files, and manages templates. |
| Student portal (this repository, port `8502`) | Student | Signs in, changes or recovers a password, follows admission progress, downloads files, and submits requested documents. |

### 1. Receive a HubSpot form

1. An applicant submits an approved HubSpot form.
2. A HubSpot workflow sends the signed form data to
   `POST /webhooks/hubspot/form-submission`.
3. CAS API validates the signature, form ID, email, and supported fields.
4. CAS API creates or updates the matching `cr65d_estudiantes` record in
   Dataverse. Repeated delivery of the same event is safe and does not create a
   duplicate student.

This flow creates or updates the student record only. It does not create a
portal password and does not send an invitation. An invalid signature, unknown
form, or invalid payload is rejected. A dependency failure returns an error so
HubSpot can retry instead of silently losing the submission.

### 2. Sign in as a CAS collaborator

1. In production, the collaborator chooses Microsoft sign-in with a `@cas.cr`
   account.
2. The portal passes the delegated Microsoft token to `POST /auth/microsoft`.
3. CAS API verifies the identity with Microsoft Graph and resolves the active
   reviewer or administrator in Dataverse.
4. The collaborator portal opens the document dashboard.

Microsoft authentication is required for collaborators in every environment,
including local development. If CAS API is unavailable or authentication
fails, the portal displays an actionable error and retry option; it must not
substitute local mock students.

### 3. Find a student and inspect progress

1. A collaborator searches by name or email and may filter by stay date or
   document status.
2. The collaborator portal calls `GET /dashboard/documents`.
3. CAS API reads the current students and document states from Dataverse.
4. The collaborator opens a student to see the six admission phases, required
   documents, versions, and review states.

An empty result is shown as an empty state. Network, permission, or Dataverse
errors are shown as errors and never converted into successful mock data.

### 4. Invite a student to the portal

1. A collaborator selects **Invite student** and supplies the student's email
   and name.
2. The collaborator portal calls `POST /student-users/temporary-access`.
3. CAS API resolves one existing student, creates or updates the linked
   `opti_portal_users` row, stores only a salted password hash, marks the account
   as requiring a password change, and sets an expiry for the temporary access.
4. CAS API sends the temporary password to the student through Resend.

The plaintext temporary password is never returned to Streamlit or written to
logs. Missing, ambiguous, or unauthorized students are rejected. If email
delivery fails, the UI reports that the invitation was not completed; it must
not claim that an email was sent.

### 5. Use a temporary password for the first time

1. The student signs in with the email and temporary password received by
   email.
2. `POST /auth/login` validates the credentials and returns
   `password_change_required=true` with a short-lived change authorization.
3. The student portal automatically opens **Create a new password**. The
   student cannot enter the dashboard first.
4. The student submits a valid new password to `POST /auth/change-password`.
5. CAS API replaces the temporary hash, clears the forced-change state, and the
   student can sign in normally.

Expired or incorrect temporary credentials are rejected without exposing
account details. Failed password changes leave the account in the forced-change
state so the temporary credential cannot accidentally become permanent.

### 6. Recover forgotten access

1. The student selects **Forgot password** and enters an email.
2. `POST /auth/forgot-password` always returns a generic response so callers
   cannot discover which emails are registered.
3. If an exact Dataverse student exists, CAS API creates the linked portal user
   when needed, generates a new temporary password, stores only its hash, and
   sends it through Resend.
4. The next successful login automatically follows the forced password-change
   flow described above.

The current implementation emails a temporary password; it does **not** email a
numeric one-time code. If delivery is not configured, the API refuses to reset
the password instead of changing it without a way for the student to receive
the credential.

### 7. Follow the admission process

1. After normal sign-in, the student portal requests
   `GET /students/{student_id}/admission-progress`.
2. CAS API verifies that the signed-in student owns the requested record.
3. The portal displays the six phases, current phase, each required document,
   and whether the next action belongs to CAS or the student.
4. Refreshing the page reads the latest authoritative state from CAS API.

A student can see only their own record and files. A missing document or phase
is displayed as unavailable, while authentication, permission, and dependency
failures are handled as errors rather than an empty successful process.

### 8. Download a template or CAS file

1. The student selects an available download action.
2. The portal requests either the global template route or
   `GET /documents/{document_id}/download`.
3. CAS API verifies the user and resource, then obtains a temporary SharePoint
   download URL or redirects to the recorded SharePoint URL.

Only documents enabled for the student's current workflow are offered. Missing,
unauthorized, or unavailable files produce a safe error and do not reveal an
internal SharePoint path or credential.

### 9. Submit a student document

1. The student selects a required file and uploads PDF, JPG, JPEG, or PNG, up to
   40 MiB.
2. The student portal performs immediate type, size, and basic binary checks.
3. CAS API repeats the validation, verifies ownership and workflow state,
   uploads a new version to SharePoint, and updates the Dataverse document row.
4. The refreshed admission view shows the document as delivered or pending
   review, according to its configured flow.

When several files are submitted, each file has an independent result. One
failed upload must not hide the successful files. Frontend validation is only
defense in depth; the API remains the security boundary and returns safe error
messages for invalid, oversized, unauthorized, or unavailable uploads.

### 10. Review, approve, or request a replacement

1. A collaborator opens a document awaiting review.
2. The collaborator downloads or inspects the current version.
3. The collaborator approves it, or requests a replacement and supplies the
   required explanation.
4. The collaborator portal sends the decision to
   `POST /documents/{document_id}/review`.
5. CAS API records the new status and reviewer in Dataverse. The result becomes
   visible in both portals on refresh.

Only a permitted reviewer can change the state. Invalid transitions, missing
replacement comments, concurrent changes, and dependency failures must return
an error without showing a false success message.

### 11. Upload CAS files and manage templates

Collaborators can upload an individual CAS file for a student and can publish a
new global or individual template version. CAS API validates the role and file,
stores a versioned object in SharePoint, updates Dataverse when applicable, and
invalidates the affected template cache. Students can only download files made
available by their configured document flow; they cannot administer templates.

### 12. Sign out and expire sessions

Each portal uses its own signed authentication cookie. Signing out clears that
portal's session. Expired, invalid, or wrong-role API tokens return the user to
the appropriate sign-in flow. A collaborator session cannot be reused as a
student session, and a student session cannot call reviewer actions.

### Explicit boundaries

- HubSpot intake does not create credentials or send the student invitation.
- The collaborator portal does not store passwords, send Resend email directly,
  or authenticate students.
- The student portal does not query Dataverse or SharePoint directly and does
  not sign its own API user tokens.
- CAS API owns all authorization and must repeat every security validation made
  by a frontend.
- Production failures must not fall back to mock users or mock documents.
- Addresses under `example.com` are suitable for data and UI testing but cannot
  receive invitation or recovery email.

## Run locally

Use the pinned Streamlit version from `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit version
```

The expected Streamlit version is `1.60.0`. Do not rely on a globally installed
Streamlit from another project; small API differences can break widgets.

Run CAS API from its own repository in terminal 1:

```powershell
cd ..\cas-api
python -m cas_api.server
```

Run only this student portal from this repository in terminal 2. Windows App
Control may block the generated `streamlit.exe`, so use the repository launcher:

```powershell
.\scripts\run_streamlit.cmd
```

To use another port:

```powershell
.\scripts\run_streamlit.cmd --port 8514
```

With `CAS_ENVIRONMENT=local`, the launcher uses `http://127.0.0.1:8502` and
does not expose the app to the local network.

Local portal values are loaded from this ignored file:

```text
.env.streamlit.local
```

Use `.env.streamlit.example` as the safe template. Dataverse, SharePoint,
Resend, HubSpot and API signing secrets belong only in the CAS API repository.
The student portal uses `CAS_ENVIRONMENT=local` for local defaults and otherwise
reads `CAS_API_BASE_URL`. It also needs `AUTH_COOKIE_SECRET`.
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

Use only a non-production test student ID. The shortcut asks CAS API to validate
that student and mint a local user token; the portal does not sign API user
tokens. Leave `CAS_TEST_STUDENT_ID` unset in production.

## CAS API

With `CAS_ENVIRONMENT=local`, the portal points to `http://127.0.0.1:8081`.
Production reads `CAS_API_BASE_URL`.

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

All authentication, password reset, invitation, Dataverse and SharePoint logic
lives in the CAS API repository. This portal contains only API clients and UI.

Password reset uses `opti_portal_users.opti_password_hash`. Only a salted
PBKDF2 hash is stored. A temporary-password marker and expiry are encoded in
that hash, so no plaintext password or additional reset table is required.
Successful temporary-password login returns a short-lived signed authorization
for one forced password change. If an exact student email exists but has no
portal-user row yet, the first reset request creates and links that student
portal account.

Configure email delivery in the CAS API repository's `.env.api.local`:

```text
CAS_API_PASSWORD_RESET_SECRET=<long random server-side secret>
RESEND_API_KEY=re_xxxxxxxxx
RESEND_FROM_EMAIL=CAS Document Portal <notifications@cas.cr>
CAS_PORTAL_URL=https://portal.yourdomain.com
```

Create a Resend sending-access API key restricted to the verified `cas.cr`
domain. Keep that key in the API service environment, never in Streamlit
secrets or browser-facing code. The reset endpoint stays unavailable until all
four settings are present, preventing a password from being replaced when no
email can be delivered.

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

The static definitions in `config/process.py` describe presentation and upload
validation rules only. Student records, document IDs, statuses and download
availability always come from CAS API.

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

## Tests

```powershell
python -m unittest discover -s tests -v
```

These tests cover the student UI contract and API client behavior. Backend auth,
email, webhook, Dataverse and SharePoint tests live in the CAS API repository.
