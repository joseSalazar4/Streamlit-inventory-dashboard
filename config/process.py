from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Iterable, List

from config.i18n import document_description, document_label, phase_subtitle, phase_title
from models.file_rule import FileRule


ALLOWED_UPLOAD_TYPES = ("pdf", "doc", "docx", "jpg", "jpeg", "png", "mp4", "mov")
PDF_ONLY = ("pdf", "doc", "docx")
PDF_AND_WORD = ("pdf", "doc", "docx")
PDF_AND_IMAGES = ("pdf", "doc", "docx", "jpg", "jpeg", "png")
VIDEO_ONLY = ("mp4", "mov")

DOCUMENT_ALLOWED_TYPES = {
    "contrato": PDF_AND_WORD,
    "agbs": PDF_AND_WORD,
    "reglas_programa": PDF_AND_WORD,
    "factura_cas": PDF_AND_WORD,
    "factura_asesoria": PDF_AND_WORD,
    "confirmacion_admision": PDF_AND_WORD,
    "recomendacion_escolar": PDF_AND_WORD,
    "certificado_salud": PDF_AND_WORD,
    "vacunas": PDF_AND_IMAGES,
    "seguro_ingles": PDF_AND_WORD,
    "carta_familia": PDF_AND_WORD,
    "collage_fotos": PDF_AND_IMAGES,
    "video_presentacion": VIDEO_ONLY,
    "nacimiento_apostilla": PDF_AND_WORD,
    "antecedentes_apostilla": PDF_AND_WORD,
    "poder": PDF_AND_WORD,
    "carta_presentacion": PDF_AND_WORD,
    "formulario_visa": PDF_AND_WORD,
    "pasaporte": PDF_AND_IMAGES,
    "sello_visa": PDF_AND_IMAGES,
    "foto_pasaporte": PDF_AND_IMAGES,
    "eticket": PDF_ONLY,
    "permiso_menor": PDF_AND_WORD,
    "elefand": PDF_AND_IMAGES,
}


DOCUMENT_COPY = {
    "formulario_f1": {
        "label": "F1",
        "description": "Completa el formulario externo con tus datos iniciales.",
        "what_is": "Es el primer formulario de solicitud para iniciar tu proceso.",
        "what_to_do": "Completa el formulario externo con tus datos iniciales.",
        "what_happens_next": "CAS revisará tu información y habilitará los siguientes pasos.",
    },
    "sobre_mi": {
        "label": "Über mich",
        "description": "Completa el formulario externo con la información solicitada.",
        "what_is": "Es tu presentación personal.",
        "what_to_do": "Completa el formulario externo con la información solicitada.",
        "what_happens_next": "CAS usará esta información como parte de la revisión inicial.",
    },
    "entrevista": {
        "label": "Entrevista",
        "description": "CAS registra internamente tu entrevista.",
        "what_is": "Es el registro de tu entrevista con CAS.",
        "what_to_do": "No necesitas subir nada aquí. CAS registrará esta información internamente.",
        "what_happens_next": "Cuando la entrevista esté registrada, CAS continuará con la siguiente etapa.",
    },
    "formulario_f2": {
        "label": "F2",
        "description": "Completa el formulario externo cuando CAS te lo indique.",
        "what_is": "Es un formulario complementario para completar la información de tu aplicación.",
        "what_to_do": "Completa el formulario externo cuando CAS te lo indique.",
        "what_happens_next": "CAS revisará la información y continuará con la fase de contrato.",
    },
    "contrato": {
        "label": "Contrato",
        "description": "Descarga el contrato, complétalo o fírmalo y vuelve a subirlo aquí.",
        "what_is": "Es tu contrato individual con CAS.",
        "what_to_do": "Descarga el contrato, léelo, fírmalo o complétalo y vuelve a subirlo aquí.",
        "what_happens_next": "CAS revisará la versión que subiste y te avisará si necesita correcciones.",
    },
    "agbs": {
        "label": "AGBs",
        "description": "Descarga el documento, complétalo o fírmalo y vuelve a subirlo aquí.",
        "what_is": "Son las condiciones generales del contrato.",
        "what_to_do": "Descarga el documento, léelo, fírmalo o complétalo y vuelve a subirlo aquí.",
        "what_happens_next": "CAS revisará que la entrega esté completa.",
    },
    "reglas_programa": {
        "label": "Reglas del programa CAS",
        "description": "Descarga el documento, complétalo o fírmalo y vuelve a subirlo aquí.",
        "what_is": "Son las reglas del programa CAS.",
        "what_to_do": "Descarga el documento, léelo, fírmalo o complétalo y vuelve a subirlo aquí.",
        "what_happens_next": "CAS revisará que la entrega esté completa.",
    },
    "factura_cas": {
        "label": "Factura CAS",
        "description": "Descarga la factura y sube aquí lo que corresponda según el proceso.",
        "what_is": "Es la factura individual de CAS para tu proceso.",
        "what_to_do": "Descarga la factura y sube aquí lo que corresponda según el proceso.",
        "what_happens_next": "CAS revisará el archivo que subiste.",
    },
    "factura_asesoria": {
        "label": "Factura de asesoría",
        "description": "Descarga la factura y sube aquí lo que corresponda según el proceso.",
        "what_is": "Es la factura individual de asesoría para tu proceso.",
        "what_to_do": "Descarga la factura y sube aquí lo que corresponda según el proceso.",
        "what_happens_next": "CAS revisará el archivo que subiste.",
    },
    "confirmacion_admision": {
        "label": "Confirmación de admisión",
        "description": "Descárgala cuando esté disponible.",
        "what_is": "Es la confirmación de admisión que CAS habilita para ti.",
        "what_to_do": "Descárgala cuando esté disponible. No necesitas subir nada.",
        "what_happens_next": "Continúas con los documentos complementarios.",
    },
    "recomendacion_escolar": {
        "label": "Informe escolar",
        "description": "Descarga la plantilla, pide al colegio que la complete y sube el archivo final.",
        "what_is": "Es un formulario escolar que debe completarse para tu proceso.",
        "what_to_do": "Descarga la plantilla, pide al colegio que la complete y sube el archivo final.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "certificado_salud": {
        "label": "Certificado de salud",
        "description": "Descarga la plantilla, complétala con tu médico y sube el archivo final.",
        "what_is": "Es el certificado de salud requerido para tu proceso.",
        "what_to_do": "Descarga la plantilla, complétala con tu médico y sube el archivo final.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "vacunas": {
        "label": "Carné de vacunación",
        "description": "Sube una copia clara del documento.",
        "what_is": "Es la copia de tu carné o cartilla de vacunación.",
        "what_to_do": "Sube una copia clara del documento.",
        "what_happens_next": "CAS revisará que sea legible.",
    },
    "seguro_ingles": {
        "label": "Confirmación de seguro en inglés",
        "description": "Sube la confirmación o póliza de seguro.",
        "what_is": "Es la confirmación o póliza de seguro en inglés.",
        "what_to_do": "Sube la confirmación o póliza de seguro.",
        "what_happens_next": "CAS revisará el documento.",
    },
    "carta_familia": {
        "label": "Carta a la familia anfitriona en español o inglés",
        "description": "Escribe y sube tu carta en español o inglés.",
        "what_is": "Es una carta personal para tu futura familia anfitriona.",
        "what_to_do": "Escribe y sube tu carta en español o inglés.",
        "what_happens_next": "CAS revisará la carta de forma general.",
    },
    "collage_fotos": {
        "label": "Collage de fotos con aprox. 5 fotos",
        "description": "Sube un collage de fotos o aproximadamente cinco fotos.",
        "what_is": "Es una presentación visual tuya para acompañar tu perfil.",
        "what_to_do": "Sube un collage de fotos o aproximadamente cinco fotos.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "video_presentacion": {
        "label": "Video de presentación de aprox. 2 min. en español o inglés",
        "description": "Sube tu video de presentación en español o inglés.",
        "what_is": "Es un video corto para presentarte.",
        "what_to_do": "Sube tu video de presentación en español o inglés.",
        "what_happens_next": "CAS revisará el video.",
    },
    "invitacion_seminario": {
        "label": "Invitación al seminario de preparación",
        "description": "Descárgala cuando esté disponible.",
        "what_is": "Es la invitación al seminario de preparación.",
        "what_to_do": "Descárgala cuando esté disponible. No necesitas subir nada.",
        "what_happens_next": "Léela y sigue las indicaciones del seminario.",
    },
    "nacimiento_apostilla": {
        "label": "Partida de nacimiento con apostilla",
        "description": "Sube una copia clara del documento.",
        "what_is": "Es tu partida de nacimiento con apostilla.",
        "what_to_do": "Sube una copia clara del documento.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "antecedentes_apostilla": {
        "label": "Certificado de antecedentes penales con apostilla",
        "description": "Sube una copia clara del documento.",
        "what_is": "Es tu certificado de antecedentes penales con apostilla.",
        "what_to_do": "Sube una copia clara del documento.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "poder": {
        "label": "Poder",
        "description": "Descarga la plantilla, complétala y súbela aquí.",
        "what_is": "Es una autorización requerida para tu trámite.",
        "what_to_do": "Descarga la plantilla, complétala y súbela aquí.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "carta_presentacion": {
        "label": "Carta de presentación / carta",
        "description": "Descarga la plantilla, complétala y súbela aquí.",
        "what_is": "Es una carta requerida para tu proceso de visa.",
        "what_to_do": "Descarga la plantilla, complétala y súbela aquí.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "formulario_visa": {
        "label": "Formulario",
        "description": "Descarga la plantilla, complétala y sube el archivo final.",
        "what_is": "Es un formulario requerido para tu proceso de visa.",
        "what_to_do": "Descarga la plantilla, complétala y sube el archivo final.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "pasaporte": {
        "label": "Escaneo del pasaporte, página de foto",
        "description": "Sube una copia clara donde se vean tu foto y tus datos.",
        "what_is": "Es el escaneo de la página de foto de tu pasaporte.",
        "what_to_do": "Sube una copia clara donde se vean tu foto y tus datos.",
        "what_happens_next": "CAS revisará que sea legible.",
    },
    "sello_visa": {
        "label": "Escaneo del sello o adhesivo de visa",
        "description": "Sube una imagen o PDF claro cuando lo tengas.",
        "what_is": "Es el escaneo del sello o adhesivo de visa.",
        "what_to_do": "Sube una imagen o PDF claro cuando lo tengas.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "foto_pasaporte": {
        "label": "Foto de pasaporte",
        "description": "Sube una foto clara y reciente.",
        "what_is": "Es una foto tipo pasaporte para tu expediente.",
        "what_to_do": "Sube una foto clara y reciente.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "perfil_familia_escuela": {
        "label": "Perfil de familia anfitriona y escuela",
        "description": "Descárgalo cuando CAS lo habilite.",
        "what_is": "Es el perfil de tu familia anfitriona y escuela.",
        "what_to_do": "Descárgalo cuando CAS lo habilite. No necesitas subir nada.",
        "what_happens_next": "Revisa la información con atención.",
    },
    "ultimas_indicaciones": {
        "label": "Últimas indicaciones",
        "description": "Descarga el documento y léelo con atención.",
        "what_is": "Son las indicaciones finales antes de tu viaje.",
        "what_to_do": "Descarga el documento y léelo con atención.",
        "what_happens_next": "Sigue las instrucciones finales de CAS.",
    },
    "lista_equipaje": {
        "label": "Lista de equipaje",
        "description": "Descárgala y úsala para organizar tu maleta.",
        "what_is": "Es una guía para preparar tu equipaje.",
        "what_to_do": "Descárgala y úsala para organizar tu maleta.",
        "what_happens_next": "No necesitas subir nada.",
    },
    "manual_cas": {
        "label": "Manual CAS",
        "description": "Descárgalo y guárdalo para consultarlo cuando lo necesites.",
        "what_is": "Es el manual de referencia de CAS.",
        "what_to_do": "Descárgalo y guárdalo para consultarlo cuando lo necesites.",
        "what_happens_next": "Úsalo como guía durante tu preparación.",
    },
    "eticket": {
        "label": "E-ticket",
        "description": "Descárgalo cuando CAS lo habilite.",
        "what_is": "Es el boleto electrónico de viaje.",
        "what_to_do": "Descárgalo cuando CAS lo habilite. No necesitas subir nada.",
        "what_happens_next": "Revísalo y guárdalo para tu viaje.",
    },
    "permiso_menor": {
        "label": "Permiso de viaje para menores",
        "description": "Descarga la plantilla, complétala y súbela aquí si aplica.",
        "what_is": "Es el permiso de viaje requerido para menores de edad.",
        "what_to_do": "Descarga la plantilla, complétala y súbela aquí si aplica.",
        "what_happens_next": "CAS revisará la entrega.",
    },
    "elefand": {
        "label": "Registro ELEFAND",
        "description": "Completa el registro indicado y sube el comprobante.",
        "what_is": "Es el comprobante de tu registro ELEFAND.",
        "what_to_do": "Descarga la plantilla o completa el registro indicado y sube el comprobante.",
        "what_happens_next": "CAS revisará la entrega.",
    },
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
    copy = DOCUMENT_COPY.get(key, {})
    display_label = str(copy.get("label") or label)
    display_description = str(copy.get("description") or description)
    return FileRule(
        key=key,
        label=document_label(key, display_label),
        description=document_description(key, display_description),
        flow_type=flow_type,
        template_scope=template_scope,
        can_student_upload=can_student_upload,
        requires_review=requires_review,
        allowed_types=DOCUMENT_ALLOWED_TYPES.get(key, ALLOWED_UPLOAD_TYPES),
        external_url=external_url,
        what_is=str(copy.get("what_is") or ""),
        what_to_do=str(copy.get("what_to_do") or display_description),
        what_happens_next=str(copy.get("what_happens_next") or ""),
    )


DEFAULT_PHASES: List[Dict[str, Any]] = [
    {
        "id": "solicitud_aplicacion",
        "number": 1,
        "order": 10,
        "title": "Solicitud / aplicación",
        "subtitle": "Primeros formularios y entrevista del estudiante.",
        "icon": "assignment",
        "status": "not_started",
        "files": [
            document("formulario_f1", "Formulario en línea F1", "Formulario inicial de aplicación.", "external_link_only", external_url="https://hubspot.com"),
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
        "subtitle": "Documentos contractuales, facturas y confirmación de admisión.",
        "icon": "contract",
        "status": "not_started",
        "files": [
            document("contrato", "Contrato firmado", "Descarga el contrato individual, firmalo y devuelve el archivo.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("agbs", "Condiciones generales / AGBs", "Descarga la plantilla, firmala y devuelve el archivo.", "global_template_student_return_review", "global", True, True),
            document("reglas_programa", "Reglas del programa CAS", "Descarga la plantilla, firmala y devuelve el archivo.", "global_template_student_return_review", "global", True, True),
            document("factura_cas", "Factura CAS", "Descarga la factura individual y devuelve el comprobante si corresponde.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("factura_asesoria", "Factura asesoria Anne", "Descarga la factura individual y devuelve el comprobante si corresponde.", "cas_upload_individual_student_return_review", "student_specific", True, True),
            document("confirmacion_admision", "Confirmación de admisión", "Archivo individual que CAS habilita para descarga.", "cas_upload_individual_download", "student_specific"),
        ],
    },
    {
        "id": "documentos_complementarios",
        "number": 3,
        "order": 30,
        "title": "Documentos complementarios",
        "subtitle": "Documentos personales, médicos y de preparación.",
        "icon": "folder_open",
        "status": "not_started",
        "files": [
            document("recomendacion_escolar", "Informe / recomendacion escolar", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("certificado_salud", "Certificado medico / de salud", "Descarga la plantilla, completala y sube el archivo.", "global_template_student_return_review", "global", True, True),
            document("vacunas", "Carne de vacunacion", "Sube la cartilla o carne de vacunacion.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("seguro_ingles", "Confirmacion de seguro en ingles", "Sube la poliza o confirmacion de seguro.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("carta_familia", "Carta a familia anfitriona", "Sube la carta en espanol o ingles.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("collage_fotos", "Collage de fotos", "Sube un collage o un archivo consolidado.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("video_presentacion", "Video de presentación", "Sube el documento o imagen autorizada para esta entrega.", "student_upload_review", can_student_upload=True, requires_review=True),
            document("invitacion_seminario", "Invitación al seminario", "Documento global disponible para descarga.", "student_download_only_global", "global"),
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
        "subtitle": "Información que CAS entrega al estudiante.",
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
        "title": "Últimas indicaciones y vuelo",
        "subtitle": "Documentos finales de viaje y salida.",
        "icon": "flight_takeoff",
        "status": "not_started",
        "files": [
            document("ultimas_indicaciones", "Últimas indicaciones", "Documento informativo final.", "student_download_only_global", "global"),
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
        return [_localized_phase(_copy_phase(phase)) for phase in DEFAULT_PHASES]

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
        merged_phases.append(_localized_phase(phase))
    return merged_phases


def document_count(phases: Iterable[Dict[str, Any]] = DEFAULT_PHASES) -> int:
    return sum(len(phase["files"]) for phase in phases)


def _copy_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    return {**phase, "files": list(phase["files"])}


def _localized_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    phase_id = str(phase["id"])
    return {
        **phase,
        "title": phase_title(phase_id, str(phase["title"])),
        "subtitle": phase_subtitle(phase_id, str(phase["subtitle"])),
    }


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
        label=document_label(rule.key, rule.label),
        flow_type=str(item.get("flow_type") or rule.flow_type),
        template_scope=str(item.get("template_scope") or rule.template_scope),
        can_student_upload=bool(item.get("can_student_upload", rule.can_student_upload)),
        requires_review=bool(item.get("requires_review", rule.requires_review)),
        allowed_types=allowed or rule.allowed_types,
        document_id=str(item.get("document_id") or "") or None,
        status=str(item.get("status") or rule.status),
        file_name=str(item.get("file_name") or "") or None,
        rejection_comment=str(item.get("rejection_comment") or "") or None,
        external_url=str(item.get("external_url") or rule.external_url or "") or None,
        template_available=item.get("template_available"),
    )
