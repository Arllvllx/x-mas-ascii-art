"""Application configuration and command-line options."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date


PALETTES: dict[str, dict[str, tuple[int, int, int]]] = {
    "classic": {
        "foliage": (64, 133, 95),
        "garland": (238, 190, 92),
        "ornament": (225, 105, 94),
        "gold": (247, 211, 125),
        "snow": (184, 207, 220),
        "gift1": (171, 83, 87),
        "gift2": (74, 128, 112),
        "gift3": (184, 143, 78),
    },
    "frost": {
        "foliage": (100, 158, 177),
        "garland": (173, 220, 232),
        "ornament": (224, 238, 244),
        "gold": (210, 233, 241),
        "snow": (193, 223, 240),
        "gift1": (97, 138, 178),
        "gift2": (112, 166, 178),
        "gift3": (177, 201, 214),
    },
    "neon": {
        "foliage": (87, 206, 147),
        "garland": (44, 230, 238),
        "ornament": (236, 69, 173),
        "gold": (247, 238, 77),
        "snow": (148, 185, 225),
        "gift1": (210, 65, 144),
        "gift2": (58, 181, 177),
        "gift3": (142, 107, 218),
    },
    "warm": {
        "foliage": (142, 114, 75),
        "garland": (250, 187, 98),
        "ornament": (216, 112, 75),
        "gold": (255, 220, 139),
        "snow": (195, 175, 149),
        "gift1": (176, 86, 62),
        "gift2": (147, 108, 65),
        "gift3": (203, 157, 83),
    },
}
THEME_NAMES = {
    "classic": "Classic Pine",
    "frost": "Frost Blue",
    "neon": "Cyberpunk Neon",
    "warm": "Warm Gold",
}


@dataclass(frozen=True)
class AppConfig:
    """Validated options shared by the application."""

    mode: str = "showcase"
    message: str = "MERRY CHRISTMAS"
    focus_minutes: int = 25
    break_minutes: int = 5
    theme: str = "classic"
    fps: int = 30
    grid_columns: int = 88
    grid_rows: int = 74
    fullscreen: bool = False
    target: date | None = None
    headless_test: bool = False


def _parse_theme(value: str) -> str:
    """Accept short palette keys or their human-readable display names."""
    normalized = value.casefold()
    for key, name in THEME_NAMES.items():
        if normalized in (key, name.casefold()):
            return key
    raise argparse.ArgumentTypeError(f"unknown theme: {value}")


def parse_args(argv: list[str] | None = None) -> AppConfig:
    """Parse and validate the supported command-line options."""
    parser = argparse.ArgumentParser(description="A Little Winter Wish — an ASCII tree desk companion")
    parser.add_argument("--mode", choices=("showcase", "focus", "countdown"), default="showcase")
    parser.add_argument("--message", default="MERRY CHRISTMAS", help="Banner text")
    parser.add_argument("--focus", type=int, default=25, metavar="MINUTES", help="Focus duration")
    parser.add_argument("--break", dest="break_minutes", type=int, default=5, metavar="MINUTES")
    parser.add_argument("--theme", type=_parse_theme, choices=tuple(PALETTES), default="classic")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--grid-width", type=int, default=88, metavar="COLUMNS")
    parser.add_argument("--grid-height", type=int, default=74, metavar="ROWS")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen mode")
    parser.add_argument("--target", type=date.fromisoformat, metavar="YYYY-MM-DD")
    parser.add_argument("--headless-test", action="store_true", help="Render two offscreen frames and exit")
    args = parser.parse_args(argv)
    if args.focus < 1:
        parser.error("--focus must be at least 1 minute")
    if args.break_minutes < 1:
        parser.error("--break must be at least 1 minute")
    if not 1 <= args.fps <= 240:
        parser.error("--fps must be between 1 and 240")
    if not 40 <= args.grid_width <= 180:
        parser.error("--grid-width must be between 40 and 180")
    if not 30 <= args.grid_height <= 120:
        parser.error("--grid-height must be between 30 and 120")
    return AppConfig(
        mode=args.mode,
        message=args.message,
        focus_minutes=args.focus,
        break_minutes=args.break_minutes,
        theme=args.theme,
        fps=args.fps,
        grid_columns=args.grid_width,
        grid_rows=args.grid_height,
        fullscreen=args.fullscreen,
        target=args.target,
        headless_test=args.headless_test,
    )
