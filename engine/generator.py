from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from config import OUTPUT_DIR, PLATFORM_CONFIGS
from engine.background import load_background_overlay, load_cover_overlay, make_background
from engine.export import ExportError, ensure_output_dir, save_slide
from engine.image_tools import contain_image, open_product_image
from engine.layout import Box, cover_boxes, pinterest_boxes, product_slide_boxes
from engine.products import PostRecord, ProductDataError, load_posts
from engine.typography import (
    centered_text,
    draw_right_aligned,
    fit_text,
    load_body_font,
    load_font,
    load_subtitle_font,
    load_title_font,
)


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

        if self.platform.name == "pinterest":
            slides = [self._create_pinterest_pin(post)]
            for index, slide in enumerate(slides, start=1):
                save_slide(slide, destination / f"slide_{index}.png")
            return

        slides = [self._create_cover(post)]

        chunks = [post.images[index : index + 4] for index in range(0, len(post.images), 4)]
        for chunk_index, chunk in enumerate(chunks, start=1):
            slides.append(self._create_product_slide(post, chunk, chunk_index))

        slides.append(self._create_cta(post))

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
        canvas.alpha_composite(fitted, (x, y))

    def _split_cover_title(self, title: str) -> tuple[str, str]:
        parts = [part for part in title.upper().split() if part]
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])

    def _create_cover(self, post: PostRecord) -> Image.Image:
        canvas = self._base_canvas()
        overlay = load_cover_overlay(self.platform.width, self.platform.height, opacity=0.5)
        if overlay is not None:
            canvas.alpha_composite(overlay)

        draw = ImageDraw.Draw(canvas)
        top_title, bottom_title = self._split_cover_title(post.title)
        top_font = fit_text(draw, top_title, 620, 92, 44, loader=load_title_font)
        bottom_font = fit_text(draw, bottom_title or top_title, 620, 92, 44, loader=load_title_font)

        if top_title:
            centered_text(
                draw,
                top_title,
                470,
                top_font,
                self.platform.text_color,
                self.platform.width,
            )

        label = Image.new("RGBA", (560, 86), (0, 0, 0, 0))
        label_draw = ImageDraw.Draw(label)
        label_draw.rounded_rectangle(
            (0, 0, 560, 86),
            radius=24,
            fill=(255, 255, 255, 245),
        )
        subtitle_font = fit_text(draw, post.subtitle.title(), 470, 54, 26, loader=load_subtitle_font)
        subtitle_bbox = subtitle_font.getbbox(post.subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
        label_draw.text(
            ((560 - subtitle_width) // 2, (86 - subtitle_height) // 2 - 5),
            post.subtitle.title(),
            font=subtitle_font,
            fill=self.platform.text_color,
        )
        canvas.alpha_composite(label, (260, 570))

        if bottom_title:
            centered_text(
                draw,
                bottom_title,
                640,
                bottom_font,
                self.platform.text_color,
                self.platform.width,
            )

        for image_path, box in zip(post.images, cover_boxes(len(post.images))):
            self._paste_product(canvas, image_path, box)

        return canvas

    def _create_pinterest_pin(self, post: PostRecord) -> Image.Image:
        canvas = self._base_canvas()
        overlay = None
        if post.background is not None:
            overlay = load_background_overlay(
                post.background,
                self.platform.width,
                self.platform.height,
                opacity=0.45,
            )
        if overlay is None:
            overlay = load_cover_overlay(self.platform.width, self.platform.height, opacity=0.35)
        if overlay is not None:
            canvas.alpha_composite(overlay)

        draw = ImageDraw.Draw(canvas)
        self._draw_pinterest_frame(draw)

        for image_path, box in zip(post.images, pinterest_boxes(len(post.images))):
            self._paste_product(canvas, image_path, box)

        title_font = fit_text(draw, post.subtitle.title(), 720, 86, 44, loader=load_title_font)
        stack_font = fit_text(draw, post.title.title(), 620, 78, 42, loader=load_body_font)

        title_y = 645
        centered_text(
            draw,
            post.subtitle.title(),
            title_y,
            title_font,
            (15, 15, 15),
            self.platform.width,
        )

        stack_lines = self._split_pinterest_title(post.title)
        current_y = title_y + 92
        for line in stack_lines:
            centered_text(
                draw,
                line,
                current_y,
                stack_font,
                (15, 15, 15),
                self.platform.width,
            )
            current_y += 78

        return canvas

    def _draw_pinterest_frame(self, draw: ImageDraw.ImageDraw) -> None:
        border_color = (178, 170, 160, 150)
        outer = (58, 58, self.platform.width - 58, self.platform.height - 58)
        draw.rounded_rectangle(outer, radius=18, outline=border_color, width=2)

    def _split_pinterest_title(self, title: str) -> list[str]:
        parts = [part for part in title.upper().split() if part]
        if len(parts) <= 2:
            return [" ".join(parts)] if parts else [""]
        mid = (len(parts) + 1) // 2
        return [" ".join(parts[:mid]), " ".join(parts[mid:])]

    def _create_product_slide(
        self,
        post: PostRecord,
        images: list[Path],
        chunk_index: int,
    ) -> Image.Image:
        canvas = self._base_canvas()
        draw = ImageDraw.Draw(canvas)

        header_font = fit_text(draw, post.title.title(), 380, 58, 34, loader=load_title_font)
        date_font = load_body_font(30)
        draw.text((105, 86), post.title.title(), font=header_font, fill=self.platform.text_color)
        draw_right_aligned(draw, post.date, 980, 92, date_font, self.platform.text_color)

        for image_path, box in zip(images, product_slide_boxes(len(images))):
            self._paste_product(canvas, image_path, box)

        return canvas

    def _create_cta(self, post: PostRecord) -> Image.Image:
        canvas = self._base_canvas()
        draw = ImageDraw.Draw(canvas)

        title_font = fit_text(draw, post.title.title(), 520, 66, 34, loader=load_title_font)
        body_font = fit_text(draw, "Alle Artikel findet ihr in meinem", 820, 56, 30, loader=load_body_font)
        date_font = load_body_font(32)

        centered_text(
            draw,
            post.title.title(),
            110,
            title_font,
            self.platform.text_color,
            self.platform.width,
        )

        lines = [
            "Alle Artikel findet ihr in meinem",
            "Amazon Storefront.",
            "Link in Bio",
        ]
        start_y = 470
        for line in lines:
            centered_text(draw, line, start_y, body_font, self.platform.text_color, self.platform.width)
            start_y += 82

        centered_text(draw, post.date, 1170, date_font, self.platform.text_color, self.platform.width)

        icon_font = load_body_font(54)
        draw.text((650, 626), "🔗", font=icon_font, fill=(130, 180, 195))
        return canvas
