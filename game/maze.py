from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Set, Tuple

from . import constants
from .vector import Vector

TilePos = Tuple[int, int]


@dataclass
class PelletSet:

    pellets: Set[TilePos]
    power_pellets: Set[TilePos]

    @classmethod
    def from_layout(cls, layout: Sequence[str]) -> "PelletSet":
        pellets: Set[TilePos] = set()
        power: Set[TilePos] = set()
        for row, line in enumerate(layout):
            for col, char in enumerate(line):
                if char == ".":
                    pellets.add((col, row))
                elif char == "o":
                    power.add((col, row))
        return cls(pellets=pellets, power_pellets=power)

    def copy(self) -> "PelletSet":
        return PelletSet(set(self.pellets), set(self.power_pellets))


class Maze:

    def __init__(self, layout: Sequence[str]) -> None:
        if not layout:
            raise ValueError("Layout must contain at least one row")
        self.layout: List[str] = list(layout)
        self.width = len(self.layout[0])
        self.height = len(self.layout)
        self._validate_layout()
        self.pellet_template = PelletSet.from_layout(self.layout)
        self.pellets = self.pellet_template.copy()
        self.player_start = self._find_character("P")
        if self.player_start is None:
            raise ValueError("Layout must contain a player start position 'P'")
        self.ghost_starts = self._find_characters("G") or [self.player_start]

    def _validate_layout(self) -> None:
        for row, line in enumerate(self.layout):
            if len(line) != self.width:
                raise ValueError(
                    f"Layout row {row} has inconsistent width ({len(line)} != {self.width})"
                )

    def _find_character(self, char: str) -> TilePos | None:
        for row, line in enumerate(self.layout):
            for col, cell in enumerate(line):
                if cell == char:
                    return (col, row)
        return None

    def _find_characters(self, char: str) -> List[TilePos]:
        positions = []
        for row, line in enumerate(self.layout):
            for col, cell in enumerate(line):
                if cell == char:
                    positions.append((col, row))
        return positions

    def reset_pellets(self) -> None:
        self.pellets = self.pellet_template.copy()

    def draw_walls(self, canvas) -> None:
        for row, line in enumerate(self.layout):
            for col, char in enumerate(line):
                if char == "#":
                    x0 = col * constants.TILE_SIZE
                    y0 = row * constants.TILE_SIZE
                    x1 = x0 + constants.TILE_SIZE
                    y1 = y0 + constants.TILE_SIZE
                    canvas.create_rectangle(
                        x0,
                        y0,
                        x1,
                        y1,
                        fill=constants.BLUE_GRAY,
                        outline=constants.NAVY,
                        tags=("wall",),
                    )

    def draw_pellets(self, canvas) -> None:
        for pellet in self.pellets.pellets:
            self._draw_pellet(canvas, pellet, radius=3)
        for pellet in self.pellets.power_pellets:
            self._draw_pellet(canvas, pellet, radius=6)

    def _draw_pellet(self, canvas, tile_pos: TilePos, radius: int) -> None:
        center = self.tile_to_pixel_center(tile_pos)
        x, y = center
        canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=constants.PELLET_YELLOW,
            outline="",
            tags=("pellet",),
        )

    def tile_to_pixel_center(self, tile_pos: TilePos) -> Tuple[int, int]:
        x, y = tile_pos
        return (
            int(x * constants.TILE_SIZE + constants.TILE_SIZE / 2),
            int(y * constants.TILE_SIZE + constants.TILE_SIZE / 2),
        )

    def pixel_to_tile(self, position: Vector) -> TilePos:
        return (int(position.x // constants.TILE_SIZE), int(position.y // constants.TILE_SIZE))

    def is_wall(self, tile_pos: TilePos) -> bool:
        x, y = tile_pos
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return True
        return self.layout[y][x] == "#"

    def is_valid_tile(self, tile_pos: TilePos) -> bool:
        x, y = tile_pos
        return 0 <= x < self.width and 0 <= y < self.height

    def collect_pellet(self, tile_pos: TilePos) -> int:
        """Collects a pellet and returns the score gained."""

        if tile_pos in self.pellets.pellets:
            self.pellets.pellets.remove(tile_pos)
            return 10
        if tile_pos in self.pellets.power_pellets:
            self.pellets.power_pellets.remove(tile_pos)
            return 50
        return 0

    def remaining_pellets(self) -> int:
        return len(self.pellets.pellets) + len(self.pellets.power_pellets)

    def wrap_position(self, position: Vector) -> Vector:
        x = position.x
        if x < 0:
            x = constants.SCREEN_WIDTH - constants.TILE_SIZE / 2
        elif x >= constants.SCREEN_WIDTH:
            x = constants.TILE_SIZE / 2
        return Vector(x, position.y)

    def available_directions(self, tile_pos: TilePos) -> List[Vector]:
        directions = []
        for direction in [Vector(1, 0), Vector(-1, 0), Vector(0, 1), Vector(0, -1)]:
            next_tile = (tile_pos[0] + int(direction.x), tile_pos[1] + int(direction.y))
            if not self.is_wall(next_tile):
                directions.append(direction)
        return directions

    def collides_with_wall(self, position: Vector, radius: float) -> bool:
        offsets = [
            Vector(-radius, -radius),
            Vector(radius, -radius),
            Vector(-radius, radius),
            Vector(radius, radius),
        ]
        for offset in offsets:
            corner = position + offset
            tile = self.pixel_to_tile(corner)
            if self.is_wall(tile):
                return True
        return False

    def ghost_spawn_points(self) -> Iterable[TilePos]:
        return list(self.ghost_starts)
