"""Color assignment helpers for simulation bodies."""

from __future__ import annotations

import colorsys

Color = tuple[int, int, int]

WHITE: Color = (255, 255, 255)


def generated_color(index: int) -> Color:
    """Return a vivid deterministic color, never white."""

    hue = (index * 0.618033988749895) % 1.0
    red, green, blue = colorsys.hsv_to_rgb(hue, 0.72, 0.95)
    return (round(red * 255), round(green * 255), round(blue * 255))


def initial_palette(count: int) -> list[Color]:
    return [generated_color(index) for index in range(count)]
