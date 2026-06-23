from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import IMAGES_DIR, MAX_PRODUCTS, MIN_PRODUCTS, OPTIONAL_IMAGE_COLUMNS, REQUIRED_COLUMNS


class ProductDataError(Exception):
    pass


@dataclass(frozen=True)
class PostRecord:
    post_id: str
    title: str
    subtitle: str
    date: str
    images: list[Path]


def load_posts(csv_path: Path) -> list[PostRecord]:
    if not csv_path.exists():
        raise ProductDataError(f"CSV not found: {csv_path}")

    try:
        dataframe = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ProductDataError(f"Could not read CSV: {csv_path}") from exc

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        raise ProductDataError(f"Missing required column: {missing_columns[0]}")

    posts: list[PostRecord] = []
    for _, row in dataframe.iterrows():
        post_id = str(row["post_id"]).strip()
        title = str(row["title"]).strip()
        subtitle = str(row["subtitle"]).strip()
        date = str(row["date"]).strip()

        image_paths: list[Path] = []
        for column in OPTIONAL_IMAGE_COLUMNS:
            value = str(row.get(column, "")).strip()
            if not value:
                continue
            image_path = IMAGES_DIR / value
            if not image_path.exists():
                raise ProductDataError(f"Image not found: {image_path}")
            image_paths.append(image_path)

        if len(image_paths) < MIN_PRODUCTS:
            raise ProductDataError(
                f"Post '{post_id}' needs at least {MIN_PRODUCTS} product image."
            )
        if len(image_paths) > MAX_PRODUCTS:
            raise ProductDataError(
                f"Post '{post_id}' supports at most {MAX_PRODUCTS} product images."
            )

        posts.append(
            PostRecord(
                post_id=post_id,
                title=title,
                subtitle=subtitle,
                date=date,
                images=image_paths,
            )
        )

    return posts
