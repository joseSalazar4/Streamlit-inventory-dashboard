from __future__ import annotations

from dataclasses import dataclass
from typing import List

@dataclass
class FileRule:
    label: str
    key: str
    required_fields: List[str]
    description: str

