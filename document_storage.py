from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentUpload:
    """Immutable student file payload submitted through the CAS API."""

    phase_id: str
    document_type_id: str
    file_name: str
    content_type: str
    data: bytes
    sha256: str

    @property
    def size(self) -> int:
        return len(self.data)


def prepare_document(
    phase_id: str,
    document_type_id: str,
    file_name: str,
    content_type: str,
    data: bytes,
) -> DocumentUpload:
    return DocumentUpload(
        phase_id=phase_id,
        document_type_id=document_type_id,
        file_name=file_name,
        content_type=content_type,
        data=data,
        sha256=hashlib.sha256(data).hexdigest(),
    )
