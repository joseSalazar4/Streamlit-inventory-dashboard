from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Iterable, List

from models.file_rule import FileRule


ALLOWED_UPLOAD_TYPES = ("pdf", "jpg", "jpeg", "png")
PDF_ONLY = ("pdf",)
PDF_AND_IMAGES = ALLOWED_UPLOAD_TYPES

DOCUMENT_ALLOWED_TYPES = {
    "contrato": PDF_ONLY,
    "agbs": PDF_ONLY,
    "reglas_programa": PDF_ONLY,
    "factura_cas": PDF_ONLY,
    "factura_asesoria": PDF_ONLY,
    "confirmacion_admision": PDF_ONLY,
    "recomendacion_escolar": PDF_ONLY,
    "certificado_salud": PDF_ONLY,
    "vacunas": PDF_AND_IMAGES,
    "seguro_ingles": PDF_ONLY,
    "carta_familia": PDF_ONLY,
    "collage_fotos": PDF_AND_IMAGES,
    "nacimiento_apostilla": PDF_ONLY,
    "antecedentes_apostilla": PDF_ONLY,
    "poder": PDF_ONLY,
    "carta_presentacion": PDF_ONLY,
    "formulario_visa": PDF_ONLY,
    "pasaporte": PDF_AND_IMAGES,
    "sello_visa": PDF_AND_IMAGES,
    "foto_pasaporte": PDF_AND_IMAGES,
    "eticket": PDF_ONLY,
    "permiso_menor": PDF_ONLY,
    "elefand": PDF_AND_IMAGES,
}


def document(
    key: str,
    label: str,
    description: str,
    flow_type: str,
    template_scope: str = "none",
    can_student_upload: bool = False,
    requires_review: bool = False,
    external_url: str | None = None,
) -> FileRule:
    return FileRule(
        key=key,
        label=label,
        description=description,
        flow_type=flow_type,
        template_scope=template_scope,
        can_student_upload=can_student_upload,
        requires_review=requires_review,
        allowed_types=DOCUMENT_ALLOWED_TYPES.get(key, ALLOWED_UPLOAD_TYPES),
        external_url=external_url,
    )


DEFAULT_PHASES: List[Dict[str, Any]] = [
    {
        "id": "solicitud_aplicacion",
        "number": 1,
        "order": 10,
        "title": "Solicitud / aplicacion",
        "subtitle": "Primeros formularios y entrevista del estudiante.",
        "icon": "assignment",
        "status": "not_started",
        "files": [
            document("formulario_f1", "Formulario en linea F1", "Formulario inicial de aplicacion.", "external_link_only", external_url="https://hubspot.com"),
            document("sobre_mi", "Sobre mi", "Perfil personal del estudiante.", "external_link_only", external_url="https://hubspot.com"),
            document("entrevista", "Entrevista", "Registro de la entrevista.", "external_link_only", external_url="https://hubspot.com"),
            document("formulario_f2", "Formulario complementario F2", "Formulario complementario del proceso.", "external_link_only", external_url="https://hubspot.com"),
        ],
    },
    {
        "id": "contrato",
        "number": 2,
        "order": 20,
        "title": "Contrato",
        "subtitle": "Documentos contractuales, facturas y confirmacion de admision.",
        "icon": "contract",
        "status": "not_started",
        "files": [
            document("contrato", "Contrato firmado", "Descarga el contrato individual, firmalo y devuelve el archivo.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("agbs", "Condiciones generales / AGBs", "Descarga la plantilla, firmala y devuelve el archivo.", "global_template_student_return_review", "global", True, True),
            document("reglas_programa", "Reglas del programa CAS", "Descarga la plantilla, firmala y devuelve el archivo.", "global_template_student_return_review", "global", True, True),
            document("factura_cas", "Factura CAS", "Descarga la factura individual y devuelve el comprobante si corresponde.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("factura_asesoria", "Factura asesoria Anne", "Descarga la factura individual y devuelve el comprobante si corresponde.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("confirmacion_admision", "Confirmacion de admision", "Archivo individual que CAS habilita para descarga.", "cas_upload_individual_download", "student_specific"),
        ],
    },
    {
        "id": "documentos_complementarios",
        "number": 3,
        "order": 30,
        "title": "Documentos complementarios",
        "subtitle": "Documentos personales, medicos y de preparacion.",
        "icon": "folder_open",
        "status": "not_started",
        "files": [
            document("recomendacion_escolar", "Informe / recomendacion escolar", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("certificado_salud", "Certificado medico / de salud", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("vacunas", "Carne de vacunacion", "Sube la cartilla o carne de vacunacion.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("seguro_ingles", "Confirmacion de seguro en ingles", "Sube la poliza o confirmacion de seguro.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("carta_familia", "Carta a familia anfitriona", "Sube la carta en espanol o ingles.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("collage_fotos", "Collage de fotos", "Sube un collage o un archivo consolidado.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("video_presentacion", "Video de presentacion", "Sube el documento o imagen autorizada para esta entrega.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("invitacion_seminario", "Invitacion al seminario", "Documento global disponible para descarga.", "student_download_only_global", "global"),
        ],
    },
    {
        "id": "documentos_visa",
        "number": 4,
        "order": 40,
        "title": "Documentos de visa",
        "subtitle": "Documentos legales y de viaje para la visa.",
        "icon": "travel_explore",
        "status": "not_started",
        "files": [
            document("nacimiento_apostilla", "Partida de nacimiento con apostilla", "Sube el certificado apostillado.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("antecedentes_apostilla", "Antecedentes penales con apostilla", "Sube el certificado apostillado.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("poder", "Poder / autorizacion", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("carta_presentacion", "Carta de presentacion", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("formulario_visa", "Formulario de visa", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("pasaporte", "Escaneo de pasaporte", "Sube la pagina del pasaporte con foto.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("sello_visa", "Escaneo del sello o adhesivo de visa", "Sube el comprobante visual de visa.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("foto_pasaporte", "Foto tipo pasaporte", "Sube una fotografia tipo pasaporte.", "student_upload_review", can_student_upload=True, requires_review=True),
        ],
    },
    {
        "id": "familia_escuela",
        "number": 5,
        "order": 50,
        "title": "Familia anfitriona y escuela",
        "subtitle": "Informacion que CAS entrega al estudiante.",
        "icon": "home_work",
        "status": "not_started",
        "files": [
            document("perfil_familia_escuela", "Perfil de familia anfitriona y escuela", "Archivo individual que CAS habilita para descarga.", "cas_upload_individual_download", "student_specific"),
        ],
    },
    {
        "id": "ultimas_indicaciones_vuelo",
        "number": 6,
        "order": 60,
        "title": "Ultimas indicaciones y vuelo",
        "subtitle": "Documentos finales de viaje y salida.",
        "icon": "flight_takeoff",
        "status": "not_started",
        "files": [
            document("ultimas_indicaciones", "Ultimas indicaciones", "Documento informativo final.", "student_download_only_global", "global"),
            document("lista_equipaje", "Lista de equipaje", "Lista de equipaje para descarga.", "student_download_only_global", "global"),
            document("manual_cas", "Manual CAS", "Manual de referencia para el estudiante.", "student_download_only_global", "global"),
            document("eticket", "E-ticket", "Boleto electronico global disponible para descarga.", "student_download_only_global", "global"),
            document("permiso_menor", "Permiso de viaje para menores", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("elefand", "Registro ELEFAND", "Descarga la plantilla y sube el comprobante completado.", "global_template_student_return_review", "global", True, True),
        ],
    },
]


def phases_from_progress(progress: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    if not progress:
        return [_copy_phase(phase) for phase in DEFAULT_PHASES]

    api_phases = {
        str(phase.get("phase_id")): phase
        for phase in progress.get("phases", [])
        if phase.get("phase_id")
    }
    merged_phases: List[Dict[str, Any]] = []
    for default_phase in DEFAULT_PHASES:
        phase = _copy_phase(default_phase)
        api_phase = api_phases.get(str(default_phase["id"]))
        if api_phase:
            phase["title"] = str(api_phase.get("phase_name") or phase["title"])
            phase["order"] = int(api_phase.get("phase_order") or phase["order"])
            phase["status"] = str(api_phase.get("status") or phase["status"])
            documents = {
                str(item.get("document_type_id")): item
                for item in api_phase.get("documents", [])
                if item.get("document_type_id")
            }
            phase["files"] = [
                _merge_document(rule, documents.get(rule.key))
                for rule in phase["files"]
            ]
        merged_phases.append(phase)
    return merged_phases


def document_count(phases: Iterable[Dict[str, Any]] = DEFAULT_PHASES) -> int:
    return sum(len(phase["files"]) for phase in phases)


def _copy_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    return {**phase, "files": list(phase["files"])}


def _merge_document(rule: FileRule, item: Dict[str, Any] | None) -> FileRule:
    if not item:
        return rule
    allowed = tuple(
        extension
        for extension in item.get("allowed_file_types", [])
        if extension in ALLOWED_UPLOAD_TYPES
    )
    return replace(
        rule,
        label=str(item.get("document_name") or rule.label),
        flow_type=str(item.get("flow_type") or rule.flow_type),
        template_scope=str(item.get("template_scope") or rule.template_scope),
        can_student_upload=bool(item.get("can_student_upload", rule.can_student_upload)),
        requires_review=bool(item.get("requires_review", rule.requires_review)),
        allowed_types=allowed or rule.allowed_types,
        document_id=str(item.get("document_id") or "") or None,
        status=str(item.get("status") or rule.status),
        file_name=str(item.get("file_name") or "") or None,
        external_url=str(item.get("external_url") or rule.external_url or "") or None,
        template_available=item.get("template_available"),
    )
