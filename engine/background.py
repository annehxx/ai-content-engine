from __future__ import annotations

from PIL import Image, ImageDraw


def make_background(width: int, height: int, color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height), color + (255,))
    draw = ImageDraw.Draw(image)
    draw.ellipse((-160, -120, 300, 280), fill=(255, 255, 255, 60))
    draw.ellipse((760, 1010, 1220, 1490), fill=(255, 255, 255, 70))
    draw.rounded_rectangle((70, 100, width - 70, height - 100), radius=42, outline=(255, 255, 255, 45), width=3)
    return image
