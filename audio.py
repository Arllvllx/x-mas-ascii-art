"""Optional synthesized completion chime; no external audio assets required."""

from __future__ import annotations

import math

import numpy as np
import pygame


class Chime:
    """Create and play a gentle two-note completion chime with NumPy."""

    def __init__(self) -> None:
        self.muted = False
        self.available = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._sound = self._make_sound()
            self.available = True
        except pygame.error as error:
            print(f"Audio unavailable: {error}")
            self._sound = None

    @staticmethod
    def _make_sound() -> pygame.mixer.Sound:
        mixer_init = pygame.mixer.get_init()
        if mixer_init is None:
            raise pygame.error("Audio mixer is not initialized")
        rate, sample_format, channels = mixer_init
        if sample_format != -16:
            raise pygame.error(f"Unsupported audio sample format: {sample_format}")
        duration = 1.15
        time_axis = np.arange(int(rate * duration), dtype=np.float32) / rate
        envelope = np.exp(-3.2 * time_axis)
        signal = (
            0.22 * np.sin(2 * math.pi * 659.25 * time_axis)
            + 0.18 * np.sin(2 * math.pi * 783.99 * time_axis)
            + 0.12 * np.sin(2 * math.pi * 987.77 * time_axis)
        ) * envelope
        samples = np.asarray(signal * 32767, dtype=np.int16)
        if channels > 1:
            samples = np.repeat(samples[:, np.newaxis], channels, axis=1)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def toggle(self) -> bool:
        """Toggle mute state and preview the chime when sound is enabled."""
        self.muted = not self.muted
        if not self.muted:
            self.play()
        return self.muted

    def play(self) -> None:
        if self.available and not self.muted and self._sound is not None:
            self._sound.play()
