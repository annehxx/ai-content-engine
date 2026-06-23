from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int


def cover_boxes() -> list[Box]:
    return [
        Box(90, 310, 220, 250),
        Box(310, 245, 250, 280),
        Box(600, 290, 210, 240),
        Box(790, 340, 200, 230),
        Box(80, 690, 230, 250),
        Box(320, 720, 230, 240),
        Box(585, 670, 220, 255),
        Box(800, 710, 200, 230),
    ]


def grid_boxes() -> list[Box]:
    return [
        Box(120, 270, 360, 360),
        Box(590, 270, 360, 360),
        Box(120, 760, 360, 360),
        Box(590, 760, 360, 360),
    ]
