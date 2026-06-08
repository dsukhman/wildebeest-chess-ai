"""Tests for board parsing, cloning, and stdout serialization."""

import io
from contextlib import redirect_stdout

from wildebeest.board import write_board


def test_parse_dimensions(start_board):
    assert start_board.turn == "W"
    assert len(start_board.grid) == 11
    assert all(len(row) == 11 for row in start_board.grid)
    assert start_board.total_time == 60000


def test_clone_is_independent(start_board):
    clone = start_board.clone()
    clone.grid[0][0] = "."
    assert start_board.grid[0][0] != "." or clone.grid[0][0] == start_board.grid[0][0]
    # mutating the clone's grid must not affect the original
    original = start_board.grid[0][0]
    clone.grid[0][0] = "?"
    assert start_board.grid[0][0] == original


def test_write_round_trips_grid(start_board):
    buf = io.StringIO()
    with redirect_stdout(buf):
        write_board(start_board)
    lines = buf.getvalue().splitlines()
    # line 0 is the turn, lines 1..11 are the grid
    grid_out = [list(line) for line in lines[1:12]]
    assert grid_out == start_board.grid
