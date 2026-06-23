from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import FONTS_DIR


def load_font(
    size: int,
    preferred_files: list[str] | None = None,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = preferred_files or ["font.ttf"]
    for font_name in font_candidates:
        custom_font = FONTS_DIR / font_name
        if custom_font.exists():
            return ImageFont.truetype(str(custom_font), size)

    for system_font in ["arial.ttf", "Arial.ttf"]:
        try:
            return ImageFont.truetype(system_font, size)
        except OSError:
            continue

    return ImageFont.load_default()


def load_title_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return load_font(size, ["title.ttf", "font.ttf"])


def load_subtitle_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return load_font(size, ["subtitle.ttf", "font.ttf"])


def load_body_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return load_font(size, ["body.ttf", "font.ttf"])


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int = 28,
    loader=load_font,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for size in range(start_size, min_size - 1, -2):
        font = loader(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return loader(min_size)


def centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
    canvas_width: int,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (canvas_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_right_aligned(
    draw: ImageDraw.ImageDraw,
    text: str,
    right_x: int,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    draw.text((right_x - width, y), text, font=font, fill=fill)
