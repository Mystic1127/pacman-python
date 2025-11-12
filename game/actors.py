"""Character logic for Pac-Man and ghosts without pygame."""

from __future__ import annotations

import math
import random
import tkinter as tk
from collections.abc import Sequence
from typing import Optional

from . import constants
from .maze import Maze, TilePos
from .vector import Vector

DIRECTIONS: tuple[Vector, ...] = (
    Vector(1, 0),
    Vector(-1, 0),
    Vector(0, 1),
    Vector(0, -1),
)


class Actor:
    """Base class for all moving characters."""

    def __init__(
        self,
        position: Vector,
        color: constants.Color,
        speed: float,
        radius: int = 8,
    ) -> None:
        self.position = position
        self.color = color
        self.speed = speed
        self.radius = radius
        self.direction = Vector(0, 0)
        self.next_direction: Optional[Vector] = None

    def update(self, dt: float, maze: Maze) -> None:
        if self.next_direction is not None:
            self._try_change_direction(maze)
        displacement = self.direction * (self.speed * dt)
        new_position = self.position + displacement
        if not maze.collides_with_wall(new_position, self.radius):
            self.position = new_position
        else:
            self._stop_at_wall(maze)
        self.position = maze.wrap_position(self.position)

    def _try_change_direction(self, maze: Maze) -> None:
        assert self.next_direction is not None
        if self.next_direction.x == self.direction.x and self.next_direction.y == self.direction.y:
            self.next_direction = None
            return
        if not self._aligned_with_grid():
            return
        tile_pos = maze.pixel_to_tile(self.position)
        target_tile = (
            tile_pos[0] + int(self.next_direction.x),
            tile_pos[1] + int(self.next_direction.y),
        )
        if maze.is_wall(target_tile):
            return
        self.direction = self.next_direction
        self.next_direction = None

    def _stop_at_wall(self, maze: Maze) -> None:
        tile_pos = maze.pixel_to_tile(self.position)
        center = maze.tile_to_pixel_center(tile_pos)
        self.position = Vector(float(center[0]), float(center[1]))
        self.direction = Vector(0, 0)

    def _aligned_with_grid(self) -> bool:
        grid_x = (self.position.x - constants.TILE_SIZE / 2) % constants.TILE_SIZE
        grid_y = (self.position.y - constants.TILE_SIZE / 2) % constants.TILE_SIZE
        return grid_x < 1 and grid_y < 1

    def draw(self, canvas, tag: str) -> None:
        x = self.position.x
        y = self.position.y
        canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill=self.color,
            outline="",
            tags=(tag,),
        )


class Player(Actor):
    def __init__(self, position: Vector) -> None:
        super().__init__(position, constants.YELLOW, speed=120)
        self.direction = Vector(-1, 0)
        self._orientation = self.direction
        self._mouth_time = 0.0

    def handle_input(self, pressed: Sequence[str]) -> None:
        direction_map = {
            "Left": Vector(-1, 0),
            "Right": Vector(1, 0),
            "Up": Vector(0, -1),
            "Down": Vector(0, 1),
        }
        for key, direction in direction_map.items():
            if key in pressed:
                self.next_direction = direction
                break

    def update(self, dt: float, maze: Maze) -> None:
        super().update(dt, maze)
        if not self.direction.is_zero():
            self._orientation = self.direction
        # Animate the mouth opening/closing.
        cycle_duration = 0.4
        self._mouth_time = (self._mouth_time + dt) % cycle_duration

    def draw(self, canvas, tag: str) -> None:
        mouth_phase = abs((self._mouth_time / 0.2) - 1)
        mouth_angle = 30 + mouth_phase * 20
        angle = math.degrees(math.atan2(-self._orientation.y, self._orientation.x))
        start = angle + mouth_angle
        extent = 360 - 2 * mouth_angle
        x = self.position.x
        y = self.position.y
        canvas.create_arc(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            start=start,
            extent=extent,
            fill=self.color,
            outline="",
            tags=(tag,),
        )


class Ghost(Actor):
    def __init__(self, position: Vector, color: constants.Color, speed: float = 90) -> None:
        super().__init__(position, color, speed)
        self.direction = random.choice(DIRECTIONS)

    def update(self, dt: float, maze: Maze) -> None:
        tile_pos = maze.pixel_to_tile(self.position)
        if self._aligned_with_grid():
            self.direction = self._choose_direction(maze, tile_pos)
        super().update(dt, maze)

    def _choose_direction(self, maze: Maze, tile_pos: TilePos) -> Vector:
        available = maze.available_directions(tile_pos)
        opposite = Vector(-self.direction.x, -self.direction.y)
        candidates = [
            direction
            for direction in available
            if not (direction.x == opposite.x and direction.y == opposite.y)
        ]
        if not candidates:
            candidates = available
        if not candidates:
            return opposite
        return random.choice(candidates)

    def draw(self, canvas, tag: str) -> None:
        x = self.position.x
        y = self.position.y
        r = self.radius
        left = x - r
        right = x + r
        top = y - r
        bottom = y + r
        canvas.create_arc(
            left,
            top,
            right,
            bottom,
            start=0,
            extent=180,
            fill=self.color,
            outline="",
            style=tk.CHORD,
            tags=(tag,),
        )
        canvas.create_rectangle(
            left,
            y,
            right,
            bottom,
            fill=self.color,
            outline="",
            tags=(tag,),
        )
        foot_width = (right - left) / 4
        for i in range(4):
            f_left = left + i * foot_width
            canvas.create_arc(
                f_left,
                y,
                f_left + foot_width,
                bottom,
                start=180,
                extent=180,
                fill=self.color,
                outline="",
                style=tk.CHORD,
                tags=(tag,),
            )
        # Eyes
        eye_radius = r * 0.3
        eye_offset_x = r * 0.4
        eye_offset_y = r * 0.1
        pupil_offset = Vector(self.direction.x * eye_radius * 0.4, self.direction.y * eye_radius * 0.4)
        for sign in (-1, 1):
            cx = x + eye_offset_x * sign
            cy = y - eye_offset_y
            canvas.create_oval(
                cx - eye_radius,
                cy - eye_radius,
                cx + eye_radius,
                cy + eye_radius,
                fill=constants.WHITE,
                outline="",
                tags=(tag,),
            )
            canvas.create_oval(
                cx - eye_radius / 2 + pupil_offset.x,
                cy - eye_radius / 2 + pupil_offset.y,
                cx + eye_radius / 2 + pupil_offset.x,
                cy + eye_radius / 2 + pupil_offset.y,
                fill="#0000AA",
                outline="",
                tags=(tag,),
            )
