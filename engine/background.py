from __future__ import annotations

from pathlib import Path

from PIL import Image

from config import BACKGROUND_FILE_CANDIDATES, BACKGROUNDS_DIR


def make_background(width: int, height: int, color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height), color + (255,))
    return image


def load_cover_overlay(width: int, height: int, opacity: float = 0.5) -> Image.Image | None:
    background_path = _find_cover_background()
    if background_path is None:
        return None

    return load_background_overlay(background_path, width, height, opacity)


def load_background_overlay(
    background_path: Path,
    width: int,
    height: int,
    opacity: float = 0.5,
) -> Image.Image | None:
    if not background_path.exists():
        return None

    image = Image.open(background_path).convert("RGBA")
    image = image.resize((width, height), Image.LANCZOS)
    alpha = image.getchannel("A").point(lambda value: int(value * opacity))
    image.putalpha(alpha)
    return image


def _find_cover_background() -> Path | None:
    for candidate in BACKGROUND_FILE_CANDIDATES:
        path = BACKGROUNDS_DIR / candidate
        if path.exists():
            return path
    return None
