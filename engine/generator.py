from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from config import OUTPUT_DIR, PLATFORM_CONFIGS
from engine.background import make_background
from engine.export import ExportError, ensure_output_dir, save_slide
from engine.image_tools import add_shadow, contain_image, open_product_image
from engine.layout import Box, cover_boxes, grid_boxes
from engine.products import PostRecord, ProductDataError, load_posts
from engine.typography import centered_text, draw_right_aligned, fit_text, load_font


class GeneratorError(Exception):
    pass


class ContentGenerator:
    def __init__(self, platform: str = "tiktok") -> None:
        if platform not in PLATFORM_CONFIGS:
            raise GeneratorError(f"Unsupported platform: {platform}")
        self.platform = PLATFORM_CONFIGS[platform]

    def generate_from_csv(self, csv_path: Path) -> int:
        try:
            posts = load_posts(csv_path)
            for post in posts:
                self._generate_post(post)
        except (ProductDataError, ExportError, OSError) as exc:
            raise GeneratorError(str(exc)) from exc

        return len(posts)

    def _generate_post(self, post: PostRecord) -> None:
        destination = OUTPUT_DIR / post.post_id
        ensure_output_dir(destination)

        slides = [
            self._create_cover(post),
            self._create_product_slide(post, start_index=0),
            self._create_product_slide(post, start_index=4),
            self._create_cta(post),
        ]

        for index, slide in enumerate(slides, start=1):
            save_slide(slide, destination / f"slide_{index}.png")

    def _base_canvas(self) -> Image.Image:
        return make_background(
            self.platform.width,
            self.platform.height,
            self.platform.background_color,
        )

    def _paste_product(self, canvas: Image.Image, image_path: Path, box: Box) -> None:
        product = open_product_image(image_path)
        fitted = contain_image(product, box.width, box.height)
        x = box.x + (box.width - fitted.width) // 2
        y = box.y + (box.height - fitted.height) // 2
        add_shadow(canvas, fitted, x, y)
        canvas.alpha_composite(fitted, (x, y))

    def _create_cover(self, post: PostRecord) -> Image.Image:
        canvas = self._base_canvas()
        draw = ImageDraw.Draw(canvas)
        title_font = fit_text(draw, post.title, 760, 88, 42)
        centered_text(
            draw,
            post.title.upper(),
            95,
            title_font,
            self.platform.text_color,
            self.platform.width,
        )

        label = Image.new("RGBA", (700, 130), (0, 0, 0, 0))
        label_draw = ImageDraw.Draw(label)
        label_draw.rounded_rectangle(
            (0, 0, 700, 130),
            radius=34,
            fill=(255, 255, 255, 235),
        )
        subtitle_font = fit_text(draw, post.subtitle, 610, 58, 28)
        subtitle_bbox = subtitle_font.getbbox(post.subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
        label_draw.text(
            ((700 - subtitle_width) // 2, (130 - subtitle_height) // 2 - 6),
            post.subtitle,
            font=subtitle_font,
            fill=self.platform.text_color,
        )
        canvas.alpha_composite(label, (190, 585))

        for image_path, box in zip(post.images, cover_boxes()):
            self._paste_product(canvas, image_path, box)

        return canvas

    def _create_product_slide(self, post: PostRecord, start_index: int) -> Image.Image:
        canvas = self._base_canvas()
        draw = ImageDraw.Draw(canvas)

        header_font = fit_text(draw, post.title, 520, 56, 32)
        date_font = load_font(28)
        draw.text((95, 95), post.title.title(), font=header_font, fill=self.platform.text_color)
        draw_right_aligned(draw, post.date, 980, 116, date_font, self.platform.text_color)

        for image_path, box in zip(post.images[start_index : start_index + 4], grid_boxes()):
            self._paste_product(canvas, image_path, box)

        return canvas

    def _create_cta(self, post: PostRecord) -> Image.Image:
        canvas = self._base_canvas()
        draw = ImageDraw.Draw(canvas)

        title_font = fit_text(draw, post.title, 760, 74, 36)
        body_font = load_font(44)
        date_font = load_font(28)

        centered_text(
            draw,
            post.title.title(),
            270,
            title_font,
            self.platform.text_color,
            self.platform.width,
        )

        lines = [
            "Alle Artikel findet ihr in meinem",
            "Amazon Storefront.",
            "Link in Bio",
        ]
        start_y = 485
        for line in lines:
            centered_text(draw, line, start_y, body_font, self.platform.text_color, self.platform.width)
            start_y += 88

        centered_text(draw, post.date, 1010, date_font, self.platform.text_color, self.platform.width)

        icon_font = load_font(48)
        draw.text((720, 661), "->", font=icon_font, fill=self.platform.text_color)
        return canvas
