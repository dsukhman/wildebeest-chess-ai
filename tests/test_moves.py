from wildebeest.board import Board
from wildebeest.moves import generate_all_moves


def test_generates_moves_from_start(start_board):
    moves = generate_all_moves(start_board)
    assert len(moves) > 0
    # each generated move is a resulting Board position
    assert all(isinstance(m, Board) for m in moves)


def test_moves_preserve_board_shape(start_board):
    for m in generate_all_moves(start_board):
        assert len(m.grid) == 11
        assert all(len(row) == 11 for row in m.grid)


def test_moves_change_the_position(start_board):
    # at least one generated move must differ from the starting grid
    assert any(m.grid != start_board.grid for m in generate_all_moves(start_board))
