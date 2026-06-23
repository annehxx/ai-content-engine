from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "input"
IMAGES_DIR = INPUT_DIR / "images"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
LOGOS_DIR = ASSETS_DIR / "logos"
BACKGROUND_FILE_CANDIDATES = [
    "cover.png",
    "cover.jpg",
    "cover.jpeg",
    "cover.webp",
]

REQUIRED_COLUMNS = [
    "post_id",
    "title",
    "subtitle",
    "date",
]

OPTIONAL_IMAGE_COLUMNS = [f"bild_{index}" for index in range(1, 9)]
MIN_PRODUCTS = 1
MAX_PRODUCTS = 8


@dataclass(frozen=True)
class PlatformConfig:
    name: str
    width: int
    height: int
    background_color: tuple[int, int, int]
    text_color: tuple[int, int, int]


PLATFORM_CONFIGS = {
    "tiktok": PlatformConfig(
        name="tiktok",
        width=1080,
        height=1350,
        background_color=(248, 246, 242),
        text_color=(145, 48, 34),
    ),
    "pinterest": PlatformConfig(
        name="pinterest",
        width=1080,
        height=1350,
        background_color=(248, 246, 242),
        text_color=(145, 48, 34),
    ),
}
