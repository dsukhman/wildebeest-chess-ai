from .constants import TRANSPORTER_POSITIONS

# =========================
# Helper Functions
# =========================

def in_bounds(r, c):
    return 0 <= r < 11 and 0 <= c < 11


def is_friendly(piece, target):
    if target in {'.', '*', '#'}:
        return False
    return piece.isupper() == target.isupper()


def is_enemy(piece, target):
    if target in {'.', '*', '#'}:
        return False
    return piece.isupper() != target.isupper()


def belongs_to_player(piece, turn):
    if piece in {'.', '*', '#'}:
        return False
    return piece.isupper() if turn == 'W' else piece.islower()

def is_walkable(board, r, c):
    if not in_bounds(r, c):
        return False
    return board.grid[r][c] in {'.', '*', '#'}

def underlying_square(r, c):
    if r == 5 and c == 5: # Jet Pack is always in the middle of the board
        return '#'
    
    if (r, c) in TRANSPORTER_POSITIONS: # Transporters are always in the same positions on the board
        return '*'
    
    return '.' # Otherwise return an empty square

def check_game_result(board):
    white_king = False
    black_king = False

    for r in range(11): # Iterate through each row on the board
        for c in range(11): # Iterate through each column on the board
            piece = board.grid[r][c] # Check if there is a white king or black king on the board
            if piece in {'K', 'W'}:
                white_king = True
            elif piece in {'k', 'w'}:
                black_king = True

    if not white_king and not black_king: # If neither player has a king, the game is a draw
        return "draw" 

    if not white_king: # If there is no white king, black wins
        return "black"

    if not black_king: # If there is no black king, white wins
        return "white"

    return None