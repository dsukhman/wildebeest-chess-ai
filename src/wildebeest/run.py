#!/usr/bin/env python3

from random import random
import time
from .board import read_board, write_board
from .ai import alphabeta, TT, EVAL_CACHE, KILLER_MOVES
from .moves import generate_all_moves

def main():
    board = read_board()
    maximizing = (board.turn == 'W')

    remaining_time = max(1, board.total_time - board.used_time)  # in ms
    time_limit = remaining_time / 1000  # convert to seconds

    start = time.time()
    best_move = None
    depth = 1
    
    TT.clear()
    EVAL_CACHE.clear()
    KILLER_MOVES.clear()
    
    while True:
        if time.time() - start > time_limit * 0.9: # stop before time runs out 
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

    if best_move is None:
        moves = generate_all_moves(board)
        if moves:
            best_move = random.choice(moves)
        else:
            best_move = board  # no legal moves

    #end = time.time()
    #print("Total time:", end - start, "seconds")
    #print("Best move value is ", value)
    
    write_board(best_move)


if __name__ == "__main__":
    main()