# Two-platform E2E result

Date: 2026-07-26  
Test student: `E2E-20260726-144203` / `e2e.20260726.144203@example.test`

## Result

PASS

- Created an active Dataverse student with a temporary password.
- Confirmed first login required a password change.
- Confirmed the student dashboard displayed the correct student and started at Phase 2.
- Confirmed Phase 1 completed, Phase 2 available, and Phases 3–6 locked.
- Uploaded the four CAS-provided Phase 2 PDFs.
- Uploaded all five required student-return Phase 2 PDFs.
- Approved four student-return documents and confirmed Phase 3 remained locked.
- Approved the fifth document and confirmed both platforms moved the student to Phase 3.
- Confirmed the student portal displayed Phase 3 as `Open phase` and Phases 4–6 remained locked.

The test student, files, and review history were intentionally retained.

## Diagnostics

- Four early approval requests returned HTTP 400 because a stale local coworker cookie identified the reviewer as `admin`, which did not match a Dataverse reviewer.
- Signing out and completing Microsoft OAuth fixed the reviewer identity; subsequent approvals used the authenticated Microsoft account and returned HTTP 200.
- SharePoint lookup requests returned HTTP 404 when target folders did not yet exist. The following create/upload operations succeeded, so these were expected lookup-before-create responses.
- The coworker app emitted a Streamlit deprecation warning: replace `st.components.v1.html` with `st.iframe`.
- No uncaught traceback, API 5xx response, or flow-blocking exception was found.

## Production recommendations

1. Do not trust a saved local reviewer cookie independently of Microsoft OAuth. On startup, validate the session identity and force sign-in if the reviewer is missing from Dataverse.
2. Keep the authenticated reviewer ID in the approval diagnostic log, but never log credentials, OAuth codes, or tokens.
3. Replace the deprecated Streamlit component call before upgrading Streamlit.
4. Treat expected SharePoint folder-missing lookups separately from actionable 404 errors to reduce diagnostic noise.

## Phase progression ownership

Phase progression should be calculated by the API from persisted document states, not advanced by the coworker or student UI. After a review is saved, the API response for admission progress should mark a phase complete only when every required document is either `approved` or a non-reviewable document is `available_for_download`. The current phase is the first phase not complete. Both portals should refetch that authoritative progress after a successful approval; the student portal must also enforce the same phase gate server-side for uploads.
