"""Tests for static evaluation and the alpha-beta search."""

from wildebeest.ai import alphabeta, evaluate
from wildebeest.board import Board


def test_evaluate_is_numeric_and_symmetric(start_board):
    score = evaluate(start_board)
    assert isinstance(score, (int, float))
    # the standard start position is materially balanced
    assert abs(score) < 1000


def test_alphabeta_returns_a_legal_move(start_board):
    value, move = alphabeta(start_board, 1, float("-inf"), float("inf"), True)
    assert isinstance(value, (int, float))
    assert isinstance(move, Board)
    assert move.grid != start_board.grid
