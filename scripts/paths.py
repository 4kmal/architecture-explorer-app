"""Portable filesystem locations shared by Explorer diagram generators."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "assets" / "editor"
ASSET_DIAGRAMS = ROOT / "assets" / "diagrams"
TEMPLATES = ROOT / "templates"
EXPORTS = ROOT / "exports" / "diagrams"
DIAGRAMS = EXPORTS


def resolve_drawio() -> Path:
    configured = os.environ.get("DRAWIO_EXE")
    candidates = [
        Path(configured).expanduser() if configured else None,
        Path(shutil.which("draw.io") or "") if shutil.which("draw.io") else None,
        Path(shutil.which("drawio") or "") if shutil.which("drawio") else None,
        Path(r"C:\Program Files\draw.io\draw.io.exe"),
        Path(r"C:\Program Files (x86)\draw.io\draw.io.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "draw.io" / "draw.io.exe",
    ]
    return next((candidate.resolve() for candidate in candidates if candidate and candidate.exists()), Path("draw.io"))


DRAWIO = resolve_drawio()


def ensure_output_directories() -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    ASSET_DIAGRAMS.mkdir(parents=True, exist_ok=True)


ensure_output_directories()
