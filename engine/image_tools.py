from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter


def contain_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((max_width, max_height), Image.LANCZOS)
    return copy


def add_shadow(
    canvas: Image.Image,
    image: Image.Image,
    x: int,
    y: int,
    blur_radius: int = 18,
    offset: tuple[int, int] = (0, 18),
    shadow_alpha: int = 85,
) -> None:
    alpha = image.getchannel("A")
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda p: shadow_alpha if p > 0 else 0))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    canvas.alpha_composite(shadow, (x + offset[0], y + offset[1]))


def open_product_image(path: Path) -> Image.Image:
    image = Image.open(path)
    return image.convert("RGBA")
