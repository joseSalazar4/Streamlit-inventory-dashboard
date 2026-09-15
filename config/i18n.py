from __future__ import annotations

import os


def german_ui_enabled() -> bool:
    environment = os.getenv("CAS_ENVIRONMENT", "local").strip().lower()
    explicit_debug = os.getenv("CAS_STREAMLIT_UI_DEBUG", "0").strip().lower()
    return environment in {"prod", "production"} and explicit_debug not in {"1", "true", "yes", "on"}


def de(default: str, german: str) -> str:
    return german if german_ui_enabled() else default


PHASE_TITLES_DE = {
    "solicitud_aplicacion": "Bewerbung",
    "contrato": "Vertrag",
    "documentos_complementarios": "Weitere Dokumente",
    "documentos_visa": "Visumsunterlagen",
    "familia_escuela": "Gastfamilien- und Schulinfos",
    "ultimas_indicaciones_vuelo": "Letzte Hinweise + Flug",
}

PHASE_SUBTITLES_DE = {
    "solicitud_aplicacion": "Online-Formulare und Interview des Schuelers.",
    "contrato": "Vertrag, AGBs, Programmregeln, Rechnungen und Aufnahmebestaetigung.",
    "documentos_complementarios": "Persoenliche, medizinische und vorbereitende Unterlagen.",
    "documentos_visa": "Rechtliche Unterlagen und Reisedokumente fuer das Visum.",
    "familia_escuela": "Informationen, die CAS fuer den Schueler bereitstellt.",
    "ultimas_indicaciones_vuelo": "Letzte Reiseunterlagen und Hinweise vor der Abreise.",
}

DOCUMENT_LABELS_DE = {
    "formulario_f1": "Online-Formular (F1)",
    "sobre_mi": "UEBER MICH",
    "entrevista": "Interview",
    "formulario_f2": "Ergaenzendes Formular (F2)",
    "contrato": "Vertrag",
    "agbs": "AGBs",
    "reglas_programa": "CAS-Programmregeln",
    "factura_cas": "Rechnung CAS",
    "factura_asesoria": "Rechnung Beratung (Anne)",
    "confirmacion_admision": "Aufnahmebestaetigung",
    "recomendacion_escolar": "Schulgutachten",
    "certificado_salud": "Gesundheitszeugnis",
    "vacunas": "Impfpass",
    "seguro_ingles": "Versicherungsbestaetigung auf Englisch",
    "carta_familia": "Brief an die Gastfamilie auf Spanisch oder Englisch",
    "collage_fotos": "Fotokollage mit ca. 5 Fotos",
    "video_presentacion": "Vorstellungsvideo ca. 2 min. auf Spanisch oder Englisch",
    "invitacion_seminario": "Einladung zum Vorbereitungsseminar",
    "nacimiento_apostilla": "Geburtsurkunde mit Apostille",
    "antecedentes_apostilla": "Fuehrungszeugnis mit Apostille",
    "poder": "Vollmacht",
    "carta_presentacion": "Anschreiben / Brief",
    "formulario_visa": "Formular",
    "pasaporte": "Scan vom Reisepass (Fotoseite)",
    "sello_visa": "Scan vom Visumsstempel/-aufkleber",
    "foto_pasaporte": "Passfoto",
    "perfil_familia_escuela": "Gastfamilien- und Schulprofil",
    "ultimas_indicaciones": "Letzte Hinweise",
    "lista_equipaje": "Packliste",
    "manual_cas": "Handbuch CAS",
    "eticket": "E-ticket",
    "permiso_menor": "Reiseerlaubnis fuer Minderjaehrige",
    "elefand": "ELEFAND-Registrierung",
}

DOCUMENT_DESCRIPTIONS_DE = {
    "formulario_f1": "Erstes Online-Bewerbungsformular.",
    "sobre_mi": "Persoenliches Profil des Schuelers.",
    "entrevista": "Interview mit CAS.",
    "formulario_f2": "Ergaenzendes Formular fuer den weiteren Prozess.",
    "contrato": "Lade deinen individuellen Vertrag herunter, unterschreibe ihn und lade die unterschriebene Version hoch.",
    "agbs": "Lade die Vorlage herunter, unterschreibe sie und lade die unterschriebene Version hoch.",
    "reglas_programa": "Lade die CAS-Programmregeln herunter, unterschreibe sie und lade die unterschriebene Version hoch.",
    "factura_cas": "Lade die individuelle Rechnung herunter und lade den Nachweis hoch, falls erforderlich.",
    "factura_asesoria": "Lade die individuelle Rechnung herunter und lade den Nachweis hoch, falls erforderlich.",
    "confirmacion_admision": "Individuelles Dokument, das CAS zum Download bereitstellt.",
    "recomendacion_escolar": "Lade das Formular herunter, lasse es ausfuellen und lade es wieder hoch.",
    "certificado_salud": "Lade das Formular herunter, lasse es ausfuellen und lade es wieder hoch.",
    "vacunas": "Lade deinen Impfpass oder Impfnachweis hoch.",
    "seguro_ingles": "Lade die Versicherungsbestaetigung auf Englisch hoch.",
    "carta_familia": "Lade deinen Brief auf Spanisch oder Englisch hoch.",
    "collage_fotos": "Lade eine Fotokollage oder eine zusammengefasste Datei hoch.",
    "video_presentacion": "Lade dein Vorstellungsvideo hoch.",
    "invitacion_seminario": "Globales Dokument zum Download.",
    "nacimiento_apostilla": "Lade die Geburtsurkunde mit Apostille hoch.",
    "antecedentes_apostilla": "Lade das Fuehrungszeugnis mit Apostille hoch.",
    "poder": "Lade die Vorlage herunter, fuelle sie aus und lade sie wieder hoch.",
    "carta_presentacion": "Lade die Vorlage herunter, fuelle sie aus und lade sie wieder hoch.",
    "formulario_visa": "Lade das Formular herunter, fuelle es aus und lade es wieder hoch.",
    "pasaporte": "Lade die Fotoseite deines Reisepasses hoch.",
    "sello_visa": "Lade den Scan des Visumsstempels oder Visumsaufklebers hoch.",
    "foto_pasaporte": "Lade ein Passfoto hoch.",
    "perfil_familia_escuela": "Individuelles Dokument, das CAS zum Download bereitstellt.",
    "ultimas_indicaciones": "Abschliessende Hinweise zum Download.",
    "lista_equipaje": "Packliste zum Download.",
    "manual_cas": "CAS-Handbuch zum Download.",
    "eticket": "Elektronisches Ticket zum Download.",
    "permiso_menor": "Lade die Vorlage herunter, fuelle sie aus und lade sie wieder hoch.",
    "elefand": "Lade die Vorlage herunter und lade den ausgefuellten Nachweis hoch.",
}


def phase_title(phase_id: str, default: str) -> str:
    return de(default, PHASE_TITLES_DE.get(phase_id, default))


def phase_subtitle(phase_id: str, default: str) -> str:
    return de(default, PHASE_SUBTITLES_DE.get(phase_id, default))


def document_label(document_id: str, default: str) -> str:
    return de(default, DOCUMENT_LABELS_DE.get(document_id, default))


def document_description(document_id: str, default: str) -> str:
    return de(default, DOCUMENT_DESCRIPTIONS_DE.get(document_id, default))
