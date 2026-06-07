#!/usr/bin/env python3

import random
import time
from . import ai
from .board import read_board, write_board
from .ai import alphabeta, TT, EVAL_CACHE, KILLER_MOVES, SearchTimeout
from .moves import generate_all_moves

def main():
    board = read_board()
    maximizing = (board.turn == 'W')

    remaining_time = max(1, board.total_time - board.used_time)  # in ms
    time_limit = remaining_time / 1000  # convert to seconds

    start = time.time()
    ai.DEADLINE = start + time_limit * 0.95

    best_move = None
    depth = 1

    TT.clear()
    EVAL_CACHE.clear()
    KILLER_MOVES.clear()

    try:
        while True:
            if time.time() - start > time_limit * 0.5:
                break

            value, move = alphabeta(
                board,
                depth,
                float('-inf'),
                float('inf'),
                maximizing
            )

            if move is not None:
                best_move = move

            depth += 1
            if depth > 5:
                break


    except SearchTimeout:
        pass
    finally:
        ai.DEADLINE = None

    if best_move is None:
        moves = generate_all_moves(board)
        if moves:
            best_move = random.choice(moves)
        else:
            best_move = board  # no legal moves

    end = time.time()
    print("Total time:", end - start, "seconds")
    print("Best move value is ", value)

    write_board(best_move)


if __name__ == "__main__":
    main()