from __future__ import annotations

import re
from typing import Tuple

from config.i18n import de


ALLOWED_FILE_TYPES = ("pdf", "doc", "docx", "jpg", "jpeg", "png", "mp4", "mov")
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024
DANGEROUS_PDF_MARKERS = (
    b"/javascript",
    b"/js",
    b"/launch",
    b"/embeddedfile",
    b"/richmedia",
    b"/openaction",
)


def safe_ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower().strip() if "." in name else ""


def validate_file(file_name: str, data: bytes) -> Tuple[bool, str]:
    extension = safe_ext(file_name)
    if extension not in ALLOWED_FILE_TYPES:
        return False, de("Only PDF, Word, JPG, JPEG, PNG, MP4, and MOV files are allowed.", "Nur PDF-, Word-, JPG-, JPEG-, PNG-, MP4- und MOV-Dateien sind erlaubt.")
    if not data:
        return False, de("The file is empty.", "Die Datei ist leer.")
    if len(data) > MAX_FILE_SIZE_BYTES:
        return False, de("The file is too large. The maximum size is 200 MB.", "Die Datei ist zu gross. Die maximale Groesse betraegt 200 MB.")
    if extension == "pdf":
        normalized = data.lstrip()
        if not normalized.startswith(b"%PDF") or b"%%EOF" not in data[-2048:]:
            return False, de("This does not appear to be a valid PDF.", "Diese Datei scheint kein gueltiges PDF zu sein.")
        lowered = data.lower()
        if any(_contains_pdf_name(lowered, marker) for marker in DANGEROUS_PDF_MARKERS):
            return False, de("This PDF contains unsupported content. Please choose a different file.", "Dieses PDF enthaelt nicht unterstuetzte Inhalte. Bitte waehle eine andere Datei.")
    if extension in {"jpg", "jpeg"}:
        if not data.startswith(b"\xff\xd8\xff") or not data.rstrip().endswith(b"\xff\xd9"):
            return False, de("This does not appear to be a valid JPG image.", "Diese Datei scheint kein gueltiges JPG-Bild zu sein.")
    if extension == "png":
        if not data.startswith(b"\x89PNG\r\n\x1a\n") or b"IEND\xaeB`\x82" not in data[-64:]:
            return False, de("This does not appear to be a valid PNG image.", "Diese Datei scheint kein gueltiges PNG-Bild zu sein.")
    if extension == "docx":
        if not data.startswith(b"PK\x03\x04") or b"word/" not in data[:200000]:
            return False, de("This does not appear to be a valid Word document.", "Diese Datei scheint kein gueltiges Word-Dokument zu sein.")
    if extension == "doc":
        if not data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            return False, de("This does not appear to be a valid Word document.", "Diese Datei scheint kein gueltiges Word-Dokument zu sein.")
    if extension in {"mp4", "mov"}:
        if b"ftyp" not in data[:32]:
            return False, de("This does not appear to be a valid video file.", "Diese Datei scheint keine gueltige Videodatei zu sein.")
    return True, de("File selected.", "Datei ausgewaehlt.")


def _contains_pdf_name(data: bytes, name: bytes) -> bool:
    delimiter = rb"(?=[\x00\t\n\f\r /<>\[\]\(\){}%])"
    return re.search(re.escape(name.lower()) + delimiter, data) is not None
