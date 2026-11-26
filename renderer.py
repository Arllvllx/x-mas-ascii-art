"""Perspective projection, character-grid Z-buffer, and Pygame presentation."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pygame

from config import PALETTES, THEME_NAMES
from scene import ChristmasScene, ScenePoint


GLYPHS = ".:-=+*#%@"
BACKGROUND = (6, 8, 13)


@dataclass
class GridFrame:
    glyphs: np.ndarray
    colors: np.ndarray
    zbuffer: np.ndarray


def project_point(
    point: tuple[float, float, float],
    rotation: float,
    columns: int = 88,
    rows: int = 74,
) -> tuple[int, int, float] | None:
    """Rotate and perspective-project one world-space point to a grid cell."""
    x, y, z = point
    cosine, sine = math.cos(rotation), math.sin(rotation)
    rotated_x = x * cosine - z * sine
    rotated_z = x * sine + z * cosine
    camera_distance = 22.0
    depth = camera_distance + rotated_z
    if depth <= 1:
        return None
    perspective = 22.0 / depth
    center_y = rows * 0.46
    scale_limit = min(
        5.15,
        max(0.5, (center_y - 1) / 5.94),
        max(0.5, (rows * 0.82 - center_y - 1) / 4.55),
        max(0.5, (columns * 0.48 - 1) / 8.4),
    )
    scale = scale_limit * perspective
    column = round(columns / 2 + rotated_x * scale)
    row = round(center_y + y * scale)
    if column < 0 or column >= columns or row < 0 or row >= rows:
        return None
    return column, row, rotated_z


def rasterize_points(
    points: list[ScenePoint],
    rotation: float,
    columns: int = 88,
    rows: int = 74,
) -> GridFrame:
    """Rasterize points into glyph/color buffers, keeping the nearest Z per cell."""
    glyphs = np.full((rows, columns), " ", dtype="<U1")
    colors = np.zeros((rows, columns, 3), dtype=np.uint8)
    zbuffer = np.full((rows, columns), -np.inf, dtype=np.float32)
    for point in points:
        projected = project_point((point.x, point.y, point.z), rotation, columns, rows)
        if projected is None:
            continue
        column, row, depth = projected
        if depth <= zbuffer[row, column]:
            continue
        zbuffer[row, column] = depth
        color = point.color
        glyph = point.glyph[:1]
        if point.kind == "tree":
            radius = math.hypot(point.x, point.z) or 1.0
            light = max(0.0, ((-0.55 * point.x) + (0.82 * point.z)) / radius)
            brightness = 0.48 + 0.52 * light
            shade = min(len(GLYPHS) - 1, max(0, round(brightness * (len(GLYPHS) - 1))))
            glyph = GLYPHS[shade]
            color = tuple(int(channel * brightness) for channel in color)
        glyphs[row, column] = glyph
        colors[row, column] = color
    return GridFrame(glyphs, colors, zbuffer)


class AsciiRenderer:
    """Draw depth-buffered 3D glyphs and the HUD to a Pygame surface."""

    def __init__(
        self,
        columns: int = 88,
        rows: int = 74,
        cell_width: int = 11,
        cell_height: int = 12,
    ) -> None:
        self.columns = columns
        self.rows = rows
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.font = pygame.font.SysFont("Menlo, Monaco, Consolas, monospace", 14, bold=True)
        self.ui_font = pygame.font.SysFont("Menlo, Monaco, Consolas, monospace", 13)
        self.small_font = pygame.font.SysFont("Menlo, Monaco, Consolas, monospace", 10)
        self._glyph_cache: dict[tuple[str, tuple[int, int, int]], pygame.Surface] = {}
        self.active_lit_glyphs = 0

    @property
    def size(self) -> tuple[int, int]:
        return self.columns * self.cell_width, self.rows * self.cell_height

    def _glyph_surface(self, glyph: str, color: tuple[int, int, int]) -> pygame.Surface:
        key = glyph, color
        if key not in self._glyph_cache:
            self._glyph_cache[key] = self.font.render(glyph, True, color)
        return self._glyph_cache[key]

    def render(
        self,
        screen: pygame.Surface,
        scene: ChristmasScene,
        progress: float,
        elapsed: float,
        rotation: float,
        theme: str,
        message: str,
        message_length: int,
        status_text: str,
        fps: float,
        paused: bool,
        wish_active: bool = False,
        sound_muted: bool = False,
    ) -> GridFrame:
        screen.fill(BACKGROUND)
        points = scene.points(progress, elapsed, rotation, theme)
        frame = rasterize_points(points, rotation, self.columns, self.rows)
        self.active_lit_glyphs = 0
        for row, column in zip(*np.nonzero(frame.glyphs != " ")):
            glyph = str(frame.glyphs[row, column])
            color = tuple(int(value) for value in frame.colors[row, column])
            if color != (42, 56, 70):
                self.active_lit_glyphs += 1
            screen.blit(self._glyph_surface(glyph, color), (column * self.cell_width, row * self.cell_height))

        self._draw_snow(screen, scene)
        self._draw_banner(screen, message, message_length, elapsed, theme)
        self._draw_status(screen, status_text, theme)
        self._draw_hud(screen, rotation, fps, paused, theme, sound_muted)
        if wish_active:
            self._text(screen, "YOUR WISH IS ON ITS WAY THROUGH THE WINTER SKY", (255, 220, 151), self.ui_font, center=True, y=screen.get_height() // 2)
        return frame

    def _draw_snow(self, screen: pygame.Surface, scene: ChristmasScene) -> None:
        color = PALETTES["frost"]["snow"]
        for flake in scene.snow:
            x = int(flake.x * screen.get_width())
            y = int(flake.y * screen.get_height())
            glyph = self._glyph_surface(flake.glyph, color)
            screen.blit(glyph, (x, y))

    def _draw_banner(
        self,
        screen: pygame.Surface,
        message: str,
        message_length: int,
        elapsed: float,
        theme: str,
    ) -> None:
        visible = message[:message_length]
        if not visible:
            return
        cell_y = self.rows - 7
        start_x = max(0, (self.columns - len(message)) // 2)
        colors = ((244, 179, 129), (232, 214, 143), (153, 205, 166), (207, 174, 218))
        if theme == "frost":
            colors = ((162, 211, 229), (218, 237, 244), (151, 185, 218))
        elif theme == "neon":
            colors = ((48, 233, 228), (241, 81, 179), (223, 237, 87))
        elif theme == "warm":
            colors = ((246, 190, 121), (226, 130, 89), (255, 221, 153))
        for index, char in enumerate(visible):
            shade = colors[int(elapsed * 2 + index * 0.35) % len(colors)]
            screen.blit(self._glyph_surface(char, shade), ((start_x + index) * self.cell_width, cell_y * self.cell_height))

    def _draw_status(self, screen: pygame.Surface, status_text: str, theme: str) -> None:
        color = PALETTES[theme]["gold"]
        text = self.ui_font.render(status_text, True, color)
        screen.blit(text, text.get_rect(center=(screen.get_width() // 2, (self.rows - 9) * self.cell_height)))

    def _draw_hud(
        self,
        screen: pygame.Surface,
        rotation: float,
        fps: float,
        paused: bool,
        theme: str,
        sound_muted: bool,
    ) -> None:
        dim = (104, 119, 137)
        left = f"{THEME_NAMES[theme].upper()}  /  {math.degrees(rotation) % 360:05.1f} DEG"
        right = f"{self.active_lit_glyphs:04d} GLYPHS  /  {fps:04.1f} FPS"
        self._text(screen, left, dim, self.small_font, x=14, y=10)
        self._text(screen, right, dim, self.small_font, x=screen.get_width() - 14, y=10, right=True)
        sound_state = "M SOUND OFF" if sound_muted else "M SOUND ON"
        hints = f"SPACE PAUSE   F FULLSCREEN   R RESTART   1/2/3 MODES   T THEME   S SAVE   {sound_state}   W WISH   ESC QUIT"
        if paused:
            hints = "PAUSED   /   " + hints
        self._text(screen, hints, dim, self.small_font, center=True, y=screen.get_height() - 18)

    @staticmethod
    def _text(
        screen: pygame.Surface,
        value: str,
        color: tuple[int, int, int],
        font: pygame.font.Font,
        x: int = 0,
        y: int = 0,
        center: bool = False,
        right: bool = False,
    ) -> None:
        surface = font.render(value, True, color)
        if center:
            rect = surface.get_rect(center=(screen.get_width() // 2, y))
        elif right:
            rect = surface.get_rect(topright=(x, y))
        else:
            rect = surface.get_rect(topleft=(x, y))
        screen.blit(surface, rect)
