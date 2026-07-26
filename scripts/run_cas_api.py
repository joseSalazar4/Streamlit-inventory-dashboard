from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from local_env import load_env_file


def resolve_api_directory(repo_root: Path, requested: str) -> Path:
    candidates = []
    if requested:
        candidates.append(Path(requested).expanduser())
    configured = os.environ.get("CAS_API_PROJECT_DIR", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend(
        [
            repo_root / "cas-api",
            repo_root / ".local" / "cas-document-platform" / "cas-api",
            repo_root.parent / "cas-document-platform" / "cas-api",
        ]
    )

    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "cas_api" / "server.py").is_file():
            return resolved

    checked = "\n".join(f"  - {candidate}" for candidate in candidates)
    raise FileNotFoundError(
        "CAS API source was not found. Checked:\n"
        f"{checked}\n"
        "Pass --api-dir or clone djwhitee/cas-document-platform into "
        ".local/cas-document-platform."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-dir", default="")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    load_env_file(repo_root / ".env.api.local")
    api_directory = resolve_api_directory(repo_root, args.api_dir)

    sys.path.insert(0, str(api_directory))
    sys.path.insert(0, str(repo_root))
    os.chdir(api_directory)
    from local_api.student_upload_server import run

    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
