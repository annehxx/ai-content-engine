from __future__ import annotations

from pathlib import Path

from PIL import Image


class ExportError(Exception):
    pass


def ensure_output_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExportError(f"Output directory could not be created: {path}") from exc


def save_slide(image: Image.Image, destination: Path) -> None:
    try:
        image.convert("RGB").save(destination, format="PNG")
    except OSError as exc:
        raise ExportError(f"Could not save slide: {destination}") from exc
