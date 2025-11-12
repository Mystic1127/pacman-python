"""Entry point for the Pac-Man Tkinter game."""

from __future__ import annotations

from game.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
