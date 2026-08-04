from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileRule:
    key: str
    label: str
    description: str
    flow_type: str
    template_scope: str
    can_student_upload: bool
    requires_review: bool
    allowed_types: tuple[str, ...] = ("pdf", "jpg", "jpeg", "png")
    document_id: str | None = None
    status: str = "not_submitted"
    file_name: str | None = None
    rejection_comment: str | None = None
    external_url: str | None = None
    template_available: bool | None = None
