import sys

class Board:
    def __init__(self, turn, grid, meta, used_time=0, total_time=60000, move_no=0):
        self.turn = turn            # 'W' or 'B'
        self.grid = grid            # 11x11 list of lists
        self.meta = meta            # last 3 lines (unchanged)
        
        self.used_time = used_time
        self.total_time = total_time
        self.move_no = move_no

        self.cart_returns = []
        self._hash = None

    def clone(self):
        return Board(
            self.turn,
            [row[:] for row in self.grid],
            self.meta[:],
            self.used_time,
            self.total_time,
            self.move_no
        )


# =========================
# Input
# =========================

def read_board():
    lines = [line.rstrip("\n") for line in sys.stdin]

    turn = lines[0]
    grid = [list(lines[i + 1]) for i in range(11)]
    meta = lines[12:15]

    used_time = int(meta[0])
    total_time = int(meta[1])
    move_no = int(meta[2])

    return Board(turn, grid, meta, used_time, total_time, move_no)

# =========================
# Output
# =========================

def write_board(board):
    # flip turn
    print(board.turn)  # print current turn (before flip)

    # board
    for row in board.grid:
        print("".join(row))

    # meta
    for line in board.meta:
        print(line)