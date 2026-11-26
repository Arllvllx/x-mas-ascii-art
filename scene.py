"""Procedural ASCII-tree geometry, decorations, snow, and wish effects."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from config import PALETTES


@dataclass(frozen=True)
class ScenePoint:
    """A 3D sample that becomes one depth-tested glyph on the character grid."""

    x: float
    y: float
    z: float
    glyph: str
    color: tuple[int, int, int]
    layer: float = 0.0
    kind: str = "tree"


@dataclass
class Snowflake:
    x: float
    y: float
    speed: float
    drift: float
    glyph: str


class ChristmasScene:
    """Create and animate deterministic 3D tree and winter-night scene data."""

    def __init__(self, seed: int = 12, snow_count: int = 100) -> None:
        self.rng = random.Random(seed)
        self.tree_points: list[ScenePoint] = []
        self.garland_points: list[ScenePoint] = []
        self.ornaments: list[ScenePoint] = []
        self.light_points: list[ScenePoint] = []
        self.gift_points: list[ScenePoint] = []
        self.star_points: list[ScenePoint] = []
        self.ground_points: list[ScenePoint] = []
        self.snow = [
            Snowflake(
                self.rng.random(),
                self.rng.random(),
                self.rng.uniform(0.035, 0.12),
                self.rng.uniform(-0.02, 0.02),
                self.rng.choice((".", "*", "+")),
            )
            for _ in range(snow_count)
        ]
        self.wish_sparks: list[list[float]] = []
        self._star_was_visible = False
        self._star_revealed_at = 0.0
        self._generate_tree()
        self._generate_garland()
        self._generate_ornaments()
        self._generate_lights()
        self._generate_gifts()
        self._generate_star()
        self._generate_ground()

    @staticmethod
    def _scaled(color: tuple[int, int, int], brightness: float) -> tuple[int, int, int]:
        return tuple(max(0, min(255, int(channel * brightness))) for channel in color)

    def _generate_tree(self) -> None:
        foliage = PALETTES["classic"]["foliage"]
        for index in range(1650):
            y = self.rng.uniform(-5.3, 4.25)
            vertical = (y + 5.3) / 9.55
            radius = (1.0 - vertical) * 4.1 + 0.12
            phase = (vertical * 9) % 1
            # Tiered branch skirts add a recognizable pine silhouette.
            tier_radius = radius * (0.76 + 0.24 * math.sin(phase * math.pi))
            angle = self.rng.uniform(0, math.tau)
            radial = tier_radius * self.rng.uniform(0.34, 1.0)
            x = radial * math.cos(angle)
            z = radial * math.sin(angle)
            branch_glyph = self.rng.choice(("v", "Y", "*", ".", "+", ":"))
            shade = self.rng.uniform(0.55, 1.0) * (0.86 + 0.14 * max(0.0, math.cos(angle - 0.8)))
            color = self._scaled(foliage, shade)
            layer = min(0.99, max(0.0, (4.25 - y) / 9.55))
            self.tree_points.append(ScenePoint(x, y, z, branch_glyph, color, layer, "tree"))

    def _generate_garland(self) -> None:
        base_color = PALETTES["classic"]["garland"]
        count = 420
        turns = 8.5
        for i in range(count):
            t = i / (count - 1)
            y = 3.9 - t * 8.7
            vertical = (y + 5.3) / 9.55
            radius = max(0.14, (1.0 - vertical) * 4.05 + 0.16) * 0.91
            angle = t * math.tau * turns
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            self.garland_points.append(
                ScenePoint(x, y, z, "~" if i % 2 else ".", base_color, 0.64, "garland")
            )

    def _generate_ornaments(self) -> None:
        colors = (PALETTES["classic"]["ornament"], PALETTES["classic"]["gold"])
        for index in range(34):
            vertical = 0.12 + self.rng.random() * 0.75
            y = 4.0 - vertical * 8.8
            radius = (1 - vertical) * 4.0 + 0.28
            angle = self.rng.uniform(0, math.tau)
            x, z = radius * math.cos(angle), radius * math.sin(angle)
            color = colors[index % len(colors)]
            glyph = self.rng.choice(("o", "O", "@"))
            self.ornaments.append(ScenePoint(x, y, z, glyph, color, 0.74, "ornament"))

    def _generate_lights(self) -> None:
        gold = PALETTES["classic"]["gold"]
        for index in range(168):
            vertical = self.rng.uniform(0.05, 0.94)
            y = 4.0 - vertical * 8.8
            radius = (1 - vertical) * 4.0 + 0.32
            angle = self.rng.uniform(0, math.tau)
            x, z = radius * math.cos(angle), radius * math.sin(angle)
            self.light_points.append(
                ScenePoint(x, y, z, "*", gold, 0.87, f"light:{index * 0.17:.3f}")
            )

    def _add_gift(
        self,
        cx: float,
        cz: float,
        size: float,
        color: tuple[int, int, int],
        layer: float,
        gift_kind: str,
    ) -> None:
        step = 0.24
        half = size / 2
        y_bottom = 4.55
        y_top = y_bottom - size * 0.78
        yy = y_bottom
        while yy >= y_top:
            for side in (-1, 1):
                for offset in self._frange(-half, half, step):
                    self.gift_points.append(ScenePoint(cx + side * half, yy, cz + offset, "#", color, layer, gift_kind))
                    self.gift_points.append(ScenePoint(cx + offset, yy, cz + side * half, "#", color, layer, gift_kind))
            yy -= step
        ribbon = PALETTES["classic"]["gold"]
        for offset in self._frange(-half, half, step):
            self.gift_points.append(ScenePoint(cx + offset, y_top - 0.02, cz, "=", ribbon, layer, f"{gift_kind}_ribbon"))
            self.gift_points.append(ScenePoint(cx, y_top - 0.02, cz + offset, "|", ribbon, layer, f"{gift_kind}_ribbon"))
        for rise in self._frange(0.0, size * 0.45, step):
            self.gift_points.append(ScenePoint(cx, y_top - rise, cz, "*", ribbon, layer, f"{gift_kind}_ribbon"))

    @staticmethod
    def _frange(start: float, stop: float, step: float) -> list[float]:
        values: list[float] = []
        value = start
        while value <= stop + step / 2:
            values.append(value)
            value += step
        return values

    def _generate_gifts(self) -> None:
        self._add_gift(-1.35, 0.1, 1.25, PALETTES["classic"]["gift1"], 0.77, "gift1")
        self._add_gift(1.35, -0.15, 1.12, PALETTES["classic"]["gift2"], 0.78, "gift2")
        self._add_gift(0.15, 1.0, 0.88, PALETTES["classic"]["gift3"], 0.80, "gift3")

    def _generate_star(self) -> None:
        gold = PALETTES["classic"]["gold"]
        vertices: list[tuple[float, float]] = []
        for i in range(10):
            radius = 0.52 if i % 2 == 0 else 0.23
            angle = -math.pi / 2 + i * math.pi / 5
            vertices.append((radius * math.cos(angle), -5.42 + radius * math.sin(angle)))
        for index in range(len(vertices)):
            x1, y1 = vertices[index]
            x2, y2 = vertices[(index + 1) % len(vertices)]
            steps = 14
            for step in range(steps):
                t = step / steps
                self.star_points.append(
                    ScenePoint(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, 0.12, "*", gold, 0.94, "star")
                )
        self.star_points.append(ScenePoint(0, -5.42, 0.15, "@", (255, 255, 240), 0.94, "star"))

    def _generate_ground(self) -> None:
        color = (42, 56, 70)
        for z in range(-9, 10, 2):
            for x in range(-10, 11, 2):
                if x == 0 and z == 0:
                    continue
                self.ground_points.append(ScenePoint(x, 4.85, z, ".", color, 0.0, "ground"))

    def points(
        self,
        progress: float,
        elapsed: float,
        rotation: float,
        theme: str,
    ) -> list[ScenePoint]:
        """Return currently revealed objects with palette and twinkle applied."""
        palette = PALETTES[theme]
        result = list(self.ground_points)
        classic_foliage = PALETTES["classic"]["foliage"]
        for point in self.tree_points:
            if point.layer <= progress:
                shade = sum(
                    point.color[channel] / classic_foliage[channel]
                    for channel in range(3)
                ) / 3
                color = self._scaled(palette["foliage"], shade)
                result.append(
                    ScenePoint(point.x, point.y, point.z, point.glyph, color, point.layer, point.kind)
                )
        if progress >= 0.64:
            result.extend(
                ScenePoint(p.x, p.y, p.z, p.glyph, palette["garland"], p.layer, p.kind)
                for p in self.garland_points
            )
        if progress >= 0.74:
            for index, point in enumerate(self.ornaments):
                tone = palette["ornament"] if index % 2 == 0 else palette["gold"]
                result.append(ScenePoint(point.x, point.y, point.z, point.glyph, tone, point.layer, point.kind))
            for point in self.gift_points:
                color = palette["gold"] if point.kind.endswith("_ribbon") else palette[point.kind]
                result.append(ScenePoint(point.x, point.y, point.z, point.glyph, color, point.layer, point.kind))
        if progress >= 0.87:
            for index, point in enumerate(self.light_points):
                twinkle = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(elapsed * 4.2 + index * 0.37))
                result.append(
                    ScenePoint(point.x, point.y, point.z, "*" if twinkle > 0.72 else ".", palette["gold"], point.layer, point.kind)
                )
        if progress >= 0.94:
            if not self._star_was_visible:
                self._star_revealed_at = elapsed
            self._star_was_visible = True
            flash = 1.7 if elapsed - self._star_revealed_at < 0.8 else 1.0 + max(0.0, math.sin(elapsed * 2.8)) * 0.65
            for point in self.star_points:
                color = (255, 255, 240) if point.glyph == "@" else palette["gold"]
                result.append(
                    ScenePoint(point.x, point.y, point.z, point.glyph, self._scaled(color, flash), point.layer, point.kind)
                )
        else:
            self._star_was_visible = False
        for spark in self.wish_sparks:
            result.append(ScenePoint(spark[0], spark[1], spark[2], "*", (255, 231, 173), 0.0, "spark"))
        return result

    def update(self, delta_seconds: float) -> None:
        """Advance the snow field and short-lived wish streaks."""
        dt = max(0.0, min(delta_seconds, 0.1))
        for flake in self.snow:
            flake.x = (flake.x + flake.drift * dt + 1.0) % 1.0
            flake.y += flake.speed * dt
            if flake.y > 1:
                flake.y = 0
                flake.x = self.rng.random()
        for spark in self.wish_sparks:
            spark[0] += spark[3] * dt
            spark[1] += spark[4] * dt
            spark[5] -= dt
        self.wish_sparks = [spark for spark in self.wish_sparks if spark[5] > 0]

    def make_wish(self) -> None:
        """Add a brief shower of golden shooting-star particles."""
        for _ in range(24):
            self.wish_sparks.append(
                [
                    self.rng.uniform(-6, 6),
                    self.rng.uniform(-4, 0),
                    self.rng.uniform(-0.2, 1.2),
                    self.rng.uniform(-2.2, 2.2),
                    self.rng.uniform(2.2, 4.5),
                    self.rng.uniform(0.8, 1.7),
                ]
            )
