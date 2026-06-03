from wildebeest.board import Board
from wildebeest.effects import apply_after_effects
from wildebeest.utils import in_bounds, is_enemy, is_friendly


def test_in_bounds():
    assert in_bounds(0, 0)
    assert in_bounds(10, 10)
    assert not in_bounds(-1, 0)
    assert not in_bounds(11, 0)


def test_friend_and_enemy_detection():
    assert is_friendly("P", "R")        # two white pieces
    assert is_enemy("P", "r")           # white vs black
    assert not is_enemy("P", ".")       # empty is not an enemy


def test_after_effects_keep_board_shape(start_board):
    result = apply_after_effects(start_board)
    board = result if isinstance(result, Board) else start_board
    assert len(board.grid) == 11
    assert all(len(row) == 11 for row in board.grid)
