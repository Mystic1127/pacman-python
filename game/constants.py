"""Constants used throughout the Pac-Man game."""

from __future__ import annotations

# Screen settings
TILE_SIZE = 20
GRID_WIDTH = 28
GRID_HEIGHT = 31
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE
FRAME_DELAY_MS = 16  # ~60 FPS

# Colors expressed as Tk-compatible hex strings
Color = str

BLACK: Color = "#000000"
NAVY: Color = "#000040"
WHITE: Color = "#FFFFFF"
YELLOW: Color = "#FFCD00"
RED: Color = "#FF0000"
CYAN: Color = "#00FFFF"
PINK: Color = "#FF69B4"
ORANGE: Color = "#FFA500"
BLUE_GRAY: Color = "#1F1F3A"
PELLET_YELLOW: Color = "#FFE07D"

# Map layout: '#' wall, '.' pellet, 'o' power pellet, ' ' empty, 'P' player start, 'G' ghost start
MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   # GGGG #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......P.......##..o.#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

# Ghost colors used sequentially
GHOST_COLORS = [RED, CYAN, PINK, ORANGE]
