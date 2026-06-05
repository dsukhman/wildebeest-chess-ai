# =========================
# Board Information
# =========================

BOARD_SIZE = 11
MIDDLE_ROW = 5
TRANSPORTER_POSITIONS = [(3,1), (3,9), (7,1), (7,9)]
EMPTY_SQUARES = frozenset({'.', '*', '#'})

# =========================
# Directions
# =========================

KING_DIRS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

KNIGHT_DIRS = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2),  (1, 2),
    (2, -1),  (2, 1),
]

ROOK_DIRS = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
]

BISHOP_DIRS = [
    (-1, -1), (-1, 1),
    (1, -1),  (1, 1),
]

# =========================
# Special Effects
# =========================

CANNOT_FLING = {'h'} 
CANNOT_BE_CAPTURED_BY_FLING = {'k', 'g', 'w'}
CANNOT_PUSH = {'g', 'w'} 
CANNOT_PUSH_GORILLA = {'g'} 
NON_POISONABLE = {'x','h'}
IMMUNE_TO_SWARM = {'x','h'}