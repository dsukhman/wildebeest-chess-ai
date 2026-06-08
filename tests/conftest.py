"""Shared pytest fixtures and the canonical starting board used across tests."""

import io
import sys
from pathlib import Path

import pytest

# Make the engine importable without installing (mirrors pyproject pythonpath).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from wildebeest.board import read_board  # noqa: E402

# Canonical 2PW starting position, White to move. Tests pin to this rather than
# examples/board.txt, which is a mutable scratch input the user may edit.
CANONICAL = """\
W
RNZBOKXBCNR
GPPSPJPPPPG
...........
.*.......*.
...........
.....#.....
...........
.*.......*.
...........
gppspjppppg
rnzbokxbcnr
0
60000
0
"""


def board_from_text(text):
    """Build a Board from a full board-state string by feeding it to read_board."""
    saved = sys.stdin
    try:
        sys.stdin = io.StringIO(text)
        return read_board()
    finally:
        sys.stdin = saved


@pytest.fixture
def start_text():
    return CANONICAL


@pytest.fixture
def start_board(start_text):
    return board_from_text(start_text)
