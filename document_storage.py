from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentUpload:
    """Immutable file payload shared by validation and future cloud storage."""

    stage_id: int
    document_key: str
    file_name: str
    content_type: str
    data: bytes
    sha256: str

    @property
    def size(self) -> int:
        return len(self.data)


def prepare_document(
    stage_id: int,
    document_key: str,
    file_name: str,
    content_type: str,
    data: bytes,
) -> DocumentUpload:
    return DocumentUpload(
        stage_id=stage_id,
        document_key=document_key,
        file_name=file_name,
        content_type=content_type,
        data=data,
        sha256=hashlib.sha256(data).hexdigest(),
    )
