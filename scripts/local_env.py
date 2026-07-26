from __future__ import annotations

import os
import re
from pathlib import Path


ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_env_file(path: Path) -> None:
    """Load a simple KEY=VALUE file without overriding terminal variables."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing local environment file: {path}. "
            f"Create it from {path.with_suffix('.example').name}."
        )

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError(f"{path.name}:{line_number} must use KEY=VALUE syntax.")

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not ENV_NAME.fullmatch(name):
            raise ValueError(f"{path.name}:{line_number} has an invalid variable name.")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(name, value)
