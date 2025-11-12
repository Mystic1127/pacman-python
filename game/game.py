"""Main game loop and orchestration for Pac-Man using Tkinter."""

from __future__ import annotations

import itertools
import time
import tkinter as tk
from enum import Enum, auto

from . import constants
from .actors import Ghost, Player
from .maze import Maze
from .vector import Vector


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class Game:
    """High level controller for the Pac-Man game."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Pac-Man")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root,
            width=constants.SCREEN_WIDTH,
            height=constants.SCREEN_HEIGHT,
            bg=constants.BLACK,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

        self.maze = Maze(constants.MAZE_LAYOUT)
        self.level = 1
        self.score = 0
        self.lives = 3
        self.state = GameState.MENU
        self.running = True
        self.last_time = time.perf_counter()
        self.pressed_keys: set[str] = set()

        self.player: Player | None = None
        self.ghosts: list[Ghost] = []
        self.walls_drawn = False

        self._create_entities()

    def _on_close(self) -> None:
        self.running = False
        self.root.destroy()

    def _create_entities(self) -> None:
        player_pos = self.maze.tile_to_pixel_center(self.maze.player_start)
        self.player = Player(Vector(float(player_pos[0]), float(player_pos[1])))
        self.player.direction = Vector(-1, 0)

        self.ghosts = []
        base_speed = 90 + (self.level - 1) * 10
        color_cycle = itertools.cycle(constants.GHOST_COLORS)
        for start in self.maze.ghost_spawn_points():
            color = next(color_cycle)
            center = self.maze.tile_to_pixel_center(start)
            ghost = Ghost(Vector(float(center[0]), float(center[1])), color, speed=base_speed)
            self.ghosts.append(ghost)

    def reset_positions(self) -> None:
        if not self.player:
            return
        player_pos = self.maze.tile_to_pixel_center(self.maze.player_start)
        self.player.position = Vector(float(player_pos[0]), float(player_pos[1]))
        self.player.direction = Vector(-1, 0)
        self.player.next_direction = None
        for ghost, start in zip(self.ghosts, self.maze.ghost_spawn_points()):
            center = self.maze.tile_to_pixel_center(start)
            ghost.position = Vector(float(center[0]), float(center[1]))
            ghost.direction = Vector(1, 0)
            ghost.next_direction = None

    def start_new_game(self) -> None:
        self.level = 1
        self.score = 0
        self.lives = 3
        self.maze.reset_pellets()
        self._create_entities()
        self.state = GameState.PLAYING
        self.pressed_keys.clear()
        self.walls_drawn = False

    def run(self) -> None:
        self.last_time = time.perf_counter()
        self._schedule_next_frame()
        self.root.mainloop()

    def _schedule_next_frame(self) -> None:
        if not self.running:
            return
        self.root.after(constants.FRAME_DELAY_MS, self._frame)

    def _frame(self) -> None:
        if not self.running:
            return
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        if self.state == GameState.PLAYING:
            self.update(dt)
        self.draw()
        self._schedule_next_frame()

    def _on_key_press(self, event: tk.Event) -> None:
        key = event.keysym
        if key == "Escape":
            self._on_close()
            return
        if self.state == GameState.MENU and key in {"Return", "space"}:
            self.start_new_game()
            return
        if self.state == GameState.GAME_OVER:
            self.start_new_game()
            return
        self.pressed_keys.add(key)

    def _on_key_release(self, event: tk.Event) -> None:
        key = event.keysym
        self.pressed_keys.discard(key)

    def update(self, dt: float) -> None:
        if not self.player:
            return
        self.player.handle_input(tuple(self.pressed_keys))
        self.player.update(dt, self.maze)
        for ghost in self.ghosts:
            ghost.update(dt, self.maze)

        tile_pos = self.maze.pixel_to_tile(self.player.position)
        self.score += self.maze.collect_pellet(tile_pos)

        if self.maze.remaining_pellets() == 0:
            self.level += 1
            self.maze.reset_pellets()
            self._create_entities()
            self.walls_drawn = False
            return

        for ghost in self.ghosts:
            if self._collides(self.player, ghost):
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.reset_positions()
                break

    def _collides(self, actor_a: Player, actor_b: Ghost) -> bool:
        return actor_a.position.distance_to(actor_b.position) < (actor_a.radius + actor_b.radius - 2)

    def draw(self) -> None:
        if not self.walls_drawn:
            self.canvas.delete("wall")
            self.maze.draw_walls(self.canvas)
            self.walls_drawn = True
        self.canvas.delete("pellet")
        self.maze.draw_pellets(self.canvas)
        self.canvas.delete("player")
        if self.player:
            self.player.draw(self.canvas, "player")
        self.canvas.delete("ghost")
        for ghost in self.ghosts:
            ghost.draw(self.canvas, "ghost")
        self.canvas.delete("hud")
        self._draw_hud()
        self.canvas.delete("overlay")
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

    def _draw_hud(self) -> None:
        self.canvas.create_text(
            10,
            10,
            text=f"Score: {self.score}",
            anchor="nw",
            fill=constants.WHITE,
            font=("Arial", 14, "bold"),
            tags=("hud",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            10,
            text=f"Level: {self.level}",
            anchor="n",
            fill=constants.WHITE,
            font=("Arial", 14, "bold"),
            tags=("hud",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH - 10,
            10,
            text=f"Lives: {self.lives}",
            anchor="ne",
            fill=constants.WHITE,
            font=("Arial", 14, "bold"),
            tags=("hud",),
        )

    def _draw_menu(self) -> None:
        self.canvas.create_rectangle(
            0,
            0,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            fill="#000000",
            stipple="gray50",
            outline="",
            tags=("overlay",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 - 40,
            text="PAC-MAN",
            fill=constants.YELLOW,
            font=("Arial", 32, "bold"),
            tags=("overlay",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2,
            text="Presiona Enter para comenzar",
            fill=constants.WHITE,
            font=("Arial", 16),
            tags=("overlay",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 + 40,
            text="Flechas para mover a Pac-Man",
            fill=constants.WHITE,
            font=("Arial", 14),
            tags=("overlay",),
        )

    def _draw_game_over(self) -> None:
        self.canvas.create_rectangle(
            0,
            0,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            fill="#000000",
            stipple="gray50",
            outline="",
            tags=("overlay",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 - 20,
            text="Juego terminado",
            fill=constants.YELLOW,
            font=("Arial", 28, "bold"),
            tags=("overlay",),
        )
        self.canvas.create_text(
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT / 2 + 20,
            text="Presiona cualquier tecla para reiniciar",
            fill=constants.WHITE,
            font=("Arial", 16),
            tags=("overlay",),
        )
