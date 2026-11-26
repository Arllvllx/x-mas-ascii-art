from datetime import date, datetime, timedelta

from renderer import project_point, rasterize_points
from scene import ChristmasScene, ScenePoint
from timer_modes import FocusTimer, countdown_target, format_countdown


def test_projection_places_center_point_in_grid() -> None:
    projected = project_point((0, 0, 0), 0)
    assert projected is not None
    assert projected[:2] == (44, 34)


def test_z_buffer_keeps_nearest_point_independent_of_draw_order() -> None:
    points = [
        ScenePoint(0, 0, -1, "x", (100, 0, 0), kind="ornament"),
        ScenePoint(0, 0, 1, "@", (0, 100, 0), kind="ornament"),
    ]
    for order in (points, list(reversed(points))):
        frame = rasterize_points(order, 0)
        assert frame.glyphs[34, 44] == "x"
        assert tuple(frame.colors[34, 44]) == (100, 0, 0)
        assert frame.zbuffer[34, 44] == -1


def test_foliage_uses_selected_palette() -> None:
    scene = ChristmasScene()
    classic = next(point for point in scene.points(0.5, 0, 0, "classic") if point.kind == "tree")
    frost = next(point for point in scene.points(0.5, 0, 0, "frost") if point.kind == "tree")
    assert classic.color != frost.color


def test_countdown_uses_christmas_then_new_year() -> None:
    before_christmas = datetime(2026, 12, 24, 23, 59, 0)
    assert countdown_target(before_christmas) == datetime(2026, 12, 25)
    christmas_day = datetime(2026, 12, 25, 12, 0, 0)
    assert countdown_target(christmas_day) == datetime(2026, 12, 25)
    after_christmas = datetime(2026, 12, 26, 0, 0, 1)
    assert countdown_target(after_christmas) == datetime(2027, 1, 1)
    assert format_countdown(timedelta(days=2, hours=3, minutes=4, seconds=5)) == "02d 03h 04m 05s"
    assert countdown_target(datetime(2026, 1, 1), date(2026, 2, 1)) == datetime(2026, 2, 1)


def test_focus_timer_progress_stages_and_completion() -> None:
    timer = FocusTimer(focus_seconds=100, break_seconds=30)
    assert timer.progress == 0
    timer.update(25)
    assert timer.progress == 0.25
    timer.update(75)
    assert timer.phase == "break"
    assert timer.progress == 1
    assert timer.completed_sessions == 1
    timer.update(30)
    assert timer.phase == "focus"
    assert timer.progress == 0
