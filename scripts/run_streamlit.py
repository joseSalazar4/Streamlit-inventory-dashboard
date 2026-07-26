from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from local_env import load_env_file


def ensure_dependencies(repo_root: Path, deps_dir: Path) -> None:
    if deps_dir.exists():
        return

    requirements = repo_root / "requirements.txt"
    print(f"Installing Python dependencies into {deps_dir} ...", flush=True)
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(deps_dir),
            "-r",
            str(requirements),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    load_env_file(repo_root / ".env.streamlit.local")
    deps_dir = repo_root / ".streamlit-python-packages"
    ensure_dependencies(repo_root, deps_dir)

    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(deps_dir))
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [str(deps_dir), str(repo_root), os.environ.get("PYTHONPATH", "")]
    )
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")

    from streamlit.web import cli as streamlit_cli

    sys.argv = [
        "streamlit",
        "run",
        str(repo_root / "main.py"),
        "--server.port",
        str(args.port),
    ]
    return int(streamlit_cli.main() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
