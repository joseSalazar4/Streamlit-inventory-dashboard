from __future__ import annotations

from typing import Any, Dict, List

from models.file_rule import FileRule


STAGES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Identity Verification",
        "subtitle": "Identity and basic information check.",
        "icon": "ID",
        "files": [
            FileRule("info_basica", "info_basica", ["nombre", "apellido"], "Debe contener nombre y apellido."),
            FileRule(
                "documento_identidad",
                "documento_identidad",
                ["numero_identificacion", "fecha_nacimiento"],
                "Debe contener numero de identificacion y fecha de nacimiento.",
            ),
            FileRule(
                "selfie_verificacion",
                "selfie_verificacion",
                [],
                "PDF de verificacion. No requiere campos de texto especificos.",
            ),
        ],
    },
    {
        "id": 2,
        "title": "Proof of Address",
        "subtitle": "Address and residency verification.",
        "icon": "AD",
        "files": [
            FileRule("comprobante_direccion", "comprobante_direccion", ["direccion", "pais"], "Debe incluir direccion completa y pais."),
            FileRule("estado_cuenta", "estado_cuenta", ["nombre_titular", "direccion"], "Debe mostrar titular y direccion."),
            FileRule("recibo_servicio", "recibo_servicio", ["fecha_emision", "direccion"], "Debe incluir fecha de emision y direccion."),
        ],
    },
    {
        "id": 3,
        "title": "Contract / Agreement",
        "subtitle": "Signed agreement and consent checks.",
        "icon": "AG",
        "files": [
            FileRule("contrato_firmado", "contrato_firmado", ["firma", "nombre_completo"], "Debe contener firma y nombre completo."),
            FileRule("anexo_terminos", "anexo_terminos", ["terminos", "condiciones"], "Debe incluir terminos y condiciones."),
            FileRule("consentimiento", "consentimiento", ["consentimiento_explicito"], "Debe declarar consentimiento explicito."),
        ],
    },
    {
        "id": 4,
        "title": "Financial Information",
        "subtitle": "Financial and bank-support documents.",
        "icon": "FI",
        "files": [
            FileRule("reporte_financiero", "reporte_financiero", ["ingresos", "egresos"], "Debe contener ingresos y egresos."),
            FileRule("datos_bancarios", "datos_bancarios", ["cuenta", "banco"], "Debe contener banco y numero de cuenta."),
            FileRule("declaracion_tributaria", "declaracion_tributaria", ["impuestos", "periodo"], "Debe incluir impuestos y periodo."),
        ],
    },
    {
        "id": 5,
        "title": "Final Review",
        "subtitle": "Final review by the team.",
        "icon": "FR",
        "files": [
            FileRule("resumen_final", "resumen_final", ["aprobacion", "estado_final"], "Debe contener aprobacion y estado final."),
            FileRule("checklist_final", "checklist_final", ["item", "verificado"], "Checklist final con items verificados."),
            FileRule("cierre_proceso", "cierre_proceso", ["cierre", "fecha"], "Debe incluir cierre y fecha."),
        ],
    },
]
