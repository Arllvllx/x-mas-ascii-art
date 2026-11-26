"""Launch the interactive ASCII Christmas tree desk companion."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pygame

from audio import Chime
from config import AppConfig, PALETTES, parse_args
from renderer import AsciiRenderer
from scene import ChristmasScene
from timer_modes import FocusTimer, MODES, ModeController


THEMES = tuple(PALETTES)


def run(config: AppConfig) -> None:
    """Run the event loop, update the active mode, and render each frame."""
    if config.headless_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    renderer = AsciiRenderer(config.grid_columns, config.grid_rows)
    windowed_size = renderer.size
    fullscreen = config.fullscreen and not config.headless_test
    display = create_display(windowed_size, fullscreen)
    canvas = pygame.Surface(renderer.size)
    pygame.display.set_caption("A Little Winter Wish — ASCII Christmas")
    clock = pygame.time.Clock()
    scene = ChristmasScene()
    focus_timer = FocusTimer(config.focus_minutes * 60, config.break_minutes * 60)
    modes = ModeController(config.mode, focus_timer, config.target, message=config.message)
    chime = Chime()
    theme_index = THEMES.index(config.theme)
    rotation = 0.0
    elapsed = 0.0
    paused = False
    wish_until = 0.0
    running = True
    frame_limit = 2 if config.headless_test else 0
    frames = 0
    while running:
        delta = min(clock.tick(config.fps) / 1000.0, 0.1)
        elapsed += delta
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    modes.restart()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    modes.set_mode(MODES[event.key - pygame.K_1])
                elif event.key == pygame.K_t:
                    theme_index = (theme_index + 1) % len(THEMES)
                elif event.key == pygame.K_s:
                    save_screenshot(canvas)
                elif event.key == pygame.K_f and not config.headless_test:
                    fullscreen = not fullscreen
                    display = create_display(windowed_size, fullscreen)
                elif event.key == pygame.K_m:
                    chime.toggle()
                elif event.key == pygame.K_w:
                    scene.make_wish()
                    wish_until = elapsed + 1.8
                elif event.key == pygame.K_LEFTBRACKET:
                    focus_timer.adjust_focus(-1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    focus_timer.adjust_focus(1)

        if not paused:
            rotation = (rotation + delta * 0.32) % (2 * 3.141592653589793)
            scene.update(delta)
        completed = modes.update(delta, paused)
        if completed:
            chime.play()
        renderer.render(
            canvas,
            scene,
            modes.progress,
            elapsed,
            rotation,
            THEMES[theme_index],
            config.message,
            modes.message_length,
            modes.status_text(),
            clock.get_fps(),
            paused,
            elapsed < wish_until,
            chime.muted,
        )
        present_frame(canvas, display)
        frames += 1
        if frame_limit and frames >= frame_limit:
            running = False
    pygame.quit()


def create_display(windowed_size: tuple[int, int], fullscreen: bool) -> pygame.Surface:
    """Create either the fixed-size window or the desktop-sized fullscreen display."""
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode(windowed_size)


def present_frame(canvas: pygame.Surface, display: pygame.Surface) -> None:
    """Scale and center the fixed-grid canvas on the current display surface."""
    if canvas.get_size() == display.get_size():
        display.blit(canvas, (0, 0))
    else:
        scale = min(
            display.get_width() / canvas.get_width(),
            display.get_height() / canvas.get_height(),
        )
        size = (round(canvas.get_width() * scale), round(canvas.get_height() * scale))
        scaled = pygame.transform.scale(canvas, size)
        display.fill((6, 8, 13))
        display.blit(scaled, scaled.get_rect(center=display.get_rect().center))
    pygame.display.flip()


def save_screenshot(screen: pygame.Surface) -> Path:
    """Save the current frame to an automatically created exports directory."""
    export_dir = Path("exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("christmas-%Y%m%d-%H%M%S.png")
    path = export_dir / filename
    pygame.image.save(screen, str(path))
    return path


def main() -> None:
    config = parse_args()
    run(config)


if __name__ == "__main__":
    main()
