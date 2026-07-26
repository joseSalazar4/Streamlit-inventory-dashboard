from __future__ import annotations

from typing import Tuple


ALLOWED_FILE_TYPES = ("pdf", "jpg", "jpeg", "png")
MAX_FILE_SIZE_BYTES = 40 * 1024 * 1024
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
        return False, "Only PDF, JPG, JPEG, and PNG files are allowed."
    if not data:
        return False, "The file is empty."
    if len(data) > MAX_FILE_SIZE_BYTES:
        return False, "The file is too large. The maximum size is 40 MB."
    if extension == "pdf":
        normalized = data.lstrip()
        if not normalized.startswith(b"%PDF") or b"%%EOF" not in data[-2048:]:
            return False, "This does not appear to be a valid PDF."
        lowered = data.lower()
        if any(marker in lowered for marker in DANGEROUS_PDF_MARKERS):
            return False, "This PDF contains unsupported content. Please choose a different file."
    if extension in {"jpg", "jpeg"}:
        if not data.startswith(b"\xff\xd8\xff") or not data.rstrip().endswith(b"\xff\xd9"):
            return False, "This does not appear to be a valid JPG image."
    if extension == "png":
        if not data.startswith(b"\x89PNG\r\n\x1a\n") or b"IEND\xaeB`\x82" not in data[-64:]:
            return False, "This does not appear to be a valid PNG image."
    return True, "File selected."
