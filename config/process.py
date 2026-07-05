from __future__ import annotations

from typing import Any, Dict, List

from models.file_rule import FileRule


def document(key: str, label: str, required_fields: List[str], description: str) -> FileRule:
    return FileRule(label=label, key=key, required_fields=required_fields, description=description)


# Replace these demo requirements with the real field checks when the final documents are ready.
IDENTITY_FILES = [
    document("info_basica", "Basic information", ["First name", "Last name"], "Must include the applicant name."),
    document("documento_identidad", "ID document", ["ID number", "Date of birth"], "Must include ID number and date of birth."),
    document("selfie_verificacion", "Selfie verification", [], "Readable PDF for visual verification."),
]

ADDRESS_FILES = [
    document("comprobante_direccion", "Proof of address", ["Full address", "Country"], "Must include current address and country."),
    document("estado_cuenta", "Account statement", ["Account holder", "Address"], "Must show account holder and address."),
    document("recibo_servicio", "Utility bill", ["Issue date", "Address"], "Must include issue date and address."),
]

CONTRACT_FILES = [
    document("contrato_firmado", "Signed contract", ["Signature", "Full legal name"], "Must include signature and full legal name."),
    document("anexo_terminos", "Terms annex", ["Terms", "Conditions"], "Must include terms and conditions."),
    document("consentimiento", "Consent form", ["Explicit consent"], "Must declare explicit consent."),
]

FINANCIAL_FILES = [
    document("reporte_financiero", "Financial report", ["Income", "Expenses"], "Must include income and expenses."),
    document("datos_bancarios", "Bank details", ["Account number", "Bank name"], "Must include bank and account number."),
    document("declaracion_tributaria", "Tax declaration", ["Tax period", "Tax amount"], "Must include tax period and amount."),
]

FINAL_REVIEW_FILES = [
    document("resumen_final", "Final summary", ["Approval", "Final status"], "Must include approval and final status."),
    document("checklist_final", "Final checklist", ["Reviewed item", "Verified status"], "Must include reviewed items and status."),
    document("cierre_proceso", "Process closeout", ["Closeout note", "Date"], "Must include closeout note and date."),
]


STAGES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Identity Verification",
        "subtitle": "Identity and basic information check.",
        "icon": "badge",
        "files": IDENTITY_FILES,
    },
    {
        "id": 2,
        "title": "Proof of Address",
        "subtitle": "Address and residency verification.",
        "icon": "location_on",
        "files": ADDRESS_FILES,
    },
    {
        "id": 3,
        "title": "Contract / Agreement",
        "subtitle": "Signed agreement and consent checks.",
        "icon": "description",
        "files": CONTRACT_FILES,
    },
    {
        "id": 4,
        "title": "Financial Information",
        "subtitle": "Financial and bank-support documents.",
        "icon": "account_balance",
        "files": FINANCIAL_FILES,
    },
    {
        "id": 5,
        "title": "Final Review",
        "subtitle": "Final review by the team.",
        "icon": "verified",
        "files": FINAL_REVIEW_FILES,
    },
]
