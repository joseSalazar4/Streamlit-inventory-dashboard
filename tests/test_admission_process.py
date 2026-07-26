from __future__ import annotations

import unittest
from unittest.mock import patch

from config.process import ALLOWED_UPLOAD_TYPES, DEFAULT_PHASES, phases_from_progress
from document_storage import prepare_document
from ui.process import (
    _download_rules,
    allowed_type_label,
    format_display_name,
    is_phase_unlocked,
)


class AdmissionProcessTests(unittest.TestCase):
    def test_display_name_normalizes_uppercase_and_lowercase_parts(self) -> None:
        self.assertEqual(format_display_name("PRUEBA Sofia Muller"), "Prueba Sofia Muller")
        self.assertEqual(format_display_name("sofía müller"), "Sofía Müller")
        self.assertEqual(format_display_name("Ana McDonald O'NEILL"), "Ana McDonald O'Neill")

    def test_student_cannot_open_a_phase_after_the_current_phase(self) -> None:
        phases = phases_from_progress(None)
        session_state = {
            "authenticated_user": {"is_test_user": False},
            "admission_progress": {
                "student": {"current_phase_id": "contrato"},
            },
        }
        with patch("ui.process.st") as streamlit:
            streamlit.session_state = session_state
            self.assertTrue(is_phase_unlocked(phases, 0))
            self.assertTrue(is_phase_unlocked(phases, 1))
            self.assertFalse(is_phase_unlocked(phases, 2))

    def test_contract_has_six_phases_and_exact_document_counts(self) -> None:
        self.assertEqual(len(DEFAULT_PHASES), 6)
        self.assertEqual(
            [len(phase["files"]) for phase in DEFAULT_PHASES],
            [4, 6, 8, 8, 1, 6],
        )
        self.assertEqual(
            [phase["id"] for phase in DEFAULT_PHASES],
            [
                "solicitud_aplicacion",
                "contrato",
                "documentos_complementarios",
                "documentos_visa",
                "familia_escuela",
                "ultimas_indicaciones_vuelo",
            ],
        )

    def test_template_routes_use_stable_document_type_ids(self) -> None:
        global_templates = {
            rule.key
            for phase in DEFAULT_PHASES
            for rule in phase["files"]
            if rule.template_scope == "global"
        }
        self.assertEqual(
            global_templates,
            {
                "agbs",
                "reglas_programa",
                "recomendacion_escolar",
                "certificado_salud",
                "invitacion_seminario",
                "poder",
                "carta_presentacion",
                "formulario_visa",
                "ultimas_indicaciones",
                "lista_equipaje",
                "manual_cas",
                "eticket",
                "permiso_menor",
                "elefand",
            },
        )

    def test_all_uploads_are_limited_to_safe_types(self) -> None:
        allowed = set(ALLOWED_UPLOAD_TYPES)
        for phase in DEFAULT_PHASES:
            for rule in phase["files"]:
                self.assertTrue(set(rule.allowed_types).issubset(allowed))

    def test_contract_uploads_are_pdf_only(self) -> None:
        contract = next(phase for phase in DEFAULT_PHASES if phase["id"] == "contrato")
        for rule in contract["files"]:
            if rule.can_student_upload:
                self.assertEqual(rule.allowed_types, ("pdf",))
                self.assertEqual(allowed_type_label(rule.allowed_types), "PDF")

    def test_downloads_are_sorted_from_shortest_label_to_longest(self) -> None:
        contract = next(phase for phase in DEFAULT_PHASES if phase["id"] == "contrato")
        labels = [rule.label for rule in _download_rules(contract)]
        self.assertEqual(
            labels,
            sorted(labels, key=lambda label: (len(label.strip()), label.casefold())),
        )

    def test_image_extensions_share_one_readable_label(self) -> None:
        self.assertEqual(
            allowed_type_label(("pdf", "jpg", "jpeg", "png")),
            "PDF / JPG / PNG",
        )

    def test_progress_response_enriches_phase_and_document(self) -> None:
        phases = phases_from_progress(
            {
                "phases": [
                    {
                        "phase_id": "contrato",
                        "phase_order": 20,
                        "phase_name": "Contrato",
                        "status": "pending_review",
                        "documents": [
                            {
                                "document_type_id": "agbs",
                                "document_id": "DOC-100",
                                "document_name": "AGBs",
                                "status": "pending_review",
                                "flow_type": "global_template_student_return_review",
                                "template_scope": "global",
                                "can_student_upload": True,
                                "requires_review": True,
                            }
                        ],
                    }
                ]
            }
        )
        contract = phases[1]
        agbs = next(rule for rule in contract["files"] if rule.key == "agbs")
        self.assertEqual(contract["status"], "pending_review")
        self.assertEqual(agbs.document_id, "DOC-100")
        self.assertEqual(agbs.status, "pending_review")
        self.assertEqual(agbs.allowed_types, ("pdf",))

    def test_prepared_document_keeps_phase_and_document_type(self) -> None:
        payload = prepare_document(
            phase_id="contrato",
            document_type_id="agbs",
            file_name="agbs.pdf",
            content_type="application/pdf",
            data=b"%PDF-1.7",
        )
        self.assertEqual(payload.phase_id, "contrato")
        self.assertEqual(payload.document_type_id, "agbs")
        self.assertEqual(
            payload.sha256,
            "86edbaa24831badfa0a8b04bb410141e2ee4182b6d0014493fe262a7a331c20b",
        )


if __name__ == "__main__":
    unittest.main()
