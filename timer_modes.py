"""State and timing logic for the tree's three desk-companion modes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


MODES = ("showcase", "focus", "countdown")
SHOWCASE_SECONDS = 15.0


def countdown_target(now: datetime, target: date | None = None) -> datetime:
    """Return the next relevant midnight: custom date, Christmas, or New Year."""
    if target is not None:
        return datetime.combine(target, time.min, tzinfo=now.tzinfo)
    christmas_date = date(now.year, 12, 25)
    christmas = datetime.combine(christmas_date, time.min, tzinfo=now.tzinfo)
    if now.date() <= christmas_date:
        return christmas
    return datetime.combine(date(now.year + 1, 1, 1), time.min, tzinfo=now.tzinfo)


def format_countdown(remaining: timedelta) -> str:
    """Format a non-negative duration as DDd HHh MMm SSs."""
    seconds = max(0, int(remaining.total_seconds()))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"


@dataclass
class FocusTimer:
    """A pausable work/break timer with a normalized build progress value."""

    focus_seconds: float = 25 * 60
    break_seconds: float = 5 * 60
    phase: str = "focus"
    elapsed: float = 0.0
    completed_sessions: int = 0

    def __post_init__(self) -> None:
        if self.focus_seconds <= 0 or self.break_seconds <= 0:
            raise ValueError("Focus and break durations must be positive")

    @property
    def duration(self) -> float:
        return self.focus_seconds if self.phase == "focus" else self.break_seconds

    @property
    def progress(self) -> float:
        """Return elapsed focus-session fraction; a break preserves the full tree."""
        if self.phase == "break":
            return 1.0
        return min(1.0, max(0.0, self.elapsed / self.focus_seconds))

    @property
    def remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed)

    def update(self, delta_seconds: float) -> bool:
        """Advance the clock; return True exactly when a work session completes."""
        if delta_seconds <= 0:
            return False
        self.elapsed += delta_seconds
        if self.elapsed < self.duration:
            return False
        self.elapsed = 0.0
        if self.phase == "focus":
            self.phase = "break"
            self.completed_sessions += 1
            return True
        self.phase = "focus"
        return False

    def reset(self) -> None:
        """Start a fresh focus session."""
        self.phase = "focus"
        self.elapsed = 0.0

    def adjust_focus(self, minutes: int) -> None:
        """Adjust focus length by whole minutes without making it invalid."""
        self.focus_seconds = max(60.0, self.focus_seconds + minutes * 60)
        if self.phase == "focus":
            self.elapsed = min(self.elapsed, self.focus_seconds)


@dataclass
class ModeController:
    """Track mode-specific elapsed time, progress, and countdown display."""

    mode: str
    focus_timer: FocusTimer
    target_date: date | None = None
    showcase_elapsed: float = 0.0
    message: str = "MERRY CHRISTMAS"
    message_elapsed: float = 0.0

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise ValueError(f"Unknown mode: {self.mode}")

    @property
    def progress(self) -> float:
        if self.mode == "focus":
            return self.focus_timer.progress
        if self.mode == "countdown":
            return 1.0
        t = min(self.showcase_elapsed, SHOWCASE_SECONDS)
        if t < 7:
            return 0.62 * t / 7
        if t < 10:
            return 0.62 + 0.12 * (t - 7) / 3
        if t < 13:
            return 0.74 + 0.19 * (t - 10) / 3
        return min(1.0, 0.93 + 0.07 * (t - 13) / 2)

    @property
    def message_length(self) -> int:
        if self.mode == "showcase":
            # The typewriter starts with the final showcase beat.
            amount = max(0.0, self.showcase_elapsed - 13.0) * 10.0
        else:
            amount = self.message_elapsed * 18
        return min(len(self.message), int(amount))

    def update(self, delta_seconds: float, paused: bool = False) -> bool:
        """Advance active clocks and return whether the focus session completed."""
        if paused:
            return False
        self.message_elapsed += delta_seconds
        if self.mode == "showcase":
            self.showcase_elapsed += delta_seconds
            if self.showcase_elapsed > SHOWCASE_SECONDS:
                self.showcase_elapsed %= SHOWCASE_SECONDS
            return False
        if self.mode == "focus":
            return self.focus_timer.update(delta_seconds)
        return False

    def restart(self) -> None:
        """Restart the current animation or work session."""
        self.showcase_elapsed = 0.0
        self.message_elapsed = 0.0
        self.focus_timer.reset()

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode
        self.showcase_elapsed = 0.0
        self.message_elapsed = 0.0
        if mode == "focus":
            self.focus_timer.reset()

    def status_text(self, now: datetime | None = None) -> str:
        if self.mode == "focus":
            seconds = int(self.focus_timer.remaining)
            minutes, seconds = divmod(seconds, 60)
            label = "FOCUS" if self.focus_timer.phase == "focus" else "BREAK"
            return f"{label}  {minutes:02d}:{seconds:02d}  ·  SESSION {self.focus_timer.completed_sessions + 1}"
        if self.mode == "countdown":
            current = now or datetime.now()
            return format_countdown(countdown_target(current, self.target_date) - current)
        return "A QUIET NIGHT  /  A WARM LIGHT  /  ONE LITTLE WISH"
