"""Perft node counts — a legality fingerprint that must not change across refactors."""

import io
import sys

from wildebeest.board import read_board
from wildebeest.moves import generate_all_moves

# Canonical 2PW starting position, White to move.
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

# depth -> expected node count from the canonical start
EXPECTED = {1: 30, 2: 899, 3: 37537}


def _canonical_board():
    saved = sys.stdin
    try:
        sys.stdin = io.StringIO(CANONICAL)
        return read_board()
    finally:
        sys.stdin = saved


def perft(board, depth):
    if depth == 0:
        return 1
    return sum(perft(m, depth - 1) for m in generate_all_moves(board))


def test_perft_depth_1():
    assert perft(_canonical_board(), 1) == EXPECTED[1]


def test_perft_depth_2():
    assert perft(_canonical_board(), 2) == EXPECTED[2]


def test_perft_depth_3():
    # ~3s; the deepest legality lock.
    assert perft(_canonical_board(), 3) == EXPECTED[3]
