import random
import time
from .constants import *
from .utils import *
from .moves import generate_all_moves

# =========================
# Global Variables
# =========================

TT = {}
EVAL_CACHE = {}
KILLER_MOVES = {}

# Node counter for benchmarking (incremented at each search node).
NODES = 0

# Wall-clock deadline (epoch seconds) for the current search; None disables it.
# When set, the search aborts with SearchTimeout once the deadline passes so a
# single deep iteration can never blow the move's time budget.
DEADLINE = None


class SearchTimeout(Exception):
    """Raised inside the search when the time deadline is exceeded."""


def time_is_up():
    # time.time() is comparatively costly, so only poll it every 256 nodes.
    return DEADLINE is not None and (NODES & 255) == 0 and time.time() >= DEADLINE

PIECE_VALUES = {
    'p': 1,      # Pawn (weak but can clog transporters)
    'b': 3,      # Bishop (long-range piece, good for control)
    'r': 5,      # Rook (strong piece, good for control and captures)
    'n': 3,      # Knight (good for forks and tricky maneuvers)

    's': 6,      # Serpent (king movement + poison)
    'o': 4,      # Old woman
    'j': 4,      # Prince Joey
    'z': 5,      # Beekeeper (paralysis is strong)

    'c': 6,      # Catapult (very strong tactical piece)
    'g': 6,      # Gorilla (board control + push mechanics)

    'e': 10,     # Grand Empress (queen + knight + serpent)

    'x': 5,      # Golf Cart
    'h': 1,      # Time machine (utility piece)

    'k': 100000,  # King must be overwhelming
    'w': 100000
}

EXPLOSION_FACTOR = 4
MAX_QUIESCENCE_DEPTH = 4

# =========================
# ZOBRIST HASHING
# =========================

ZOBRIST_TABLE = {}
ZOBRIST_SIDE = random.getrandbits(64)

ALL_PIECES = list(PIECE_VALUES.keys()) + [p.upper() for p in PIECE_VALUES.keys()]

def init_zobrist():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for piece in ALL_PIECES:
                ZOBRIST_TABLE[(r, c, piece)] = random.getrandbits(64)

# Call once at startup
init_zobrist()

# =========================
# Evaluate
# =========================

def evaluate(board):
    grid = board.grid
    score = 0

    white_king = None
    black_king = None

    serpents = []
    beekeepers = []
    joeys = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = grid[r][c]

            if piece in {'.', '*', '#'}:
                continue

            is_white = piece.isupper()
            pl = piece.lower()

            val = PIECE_VALUES.get(pl, 0)

            if 3 <= r <= 7 and 3 <= c <= 7:
                val += 1.0

            if (r, c) in [(3,1), (3,9), (7,1), (7,9)]:
                val += 1.5

            if pl == 'p':
                val += (r if is_white else (10 - r)) * 0.2

            if is_white:
                score += val
            else:
                score -= val

            # Track important pieces
            if pl == 'k':
                if is_white:
                    white_king = (r, c)
                else:
                    black_king = (r, c)

            elif pl == 's':
                serpents.append((r, c, is_white))

            elif pl == 'z':
                beekeepers.append((r, c, is_white))

            elif pl == 'j':
                joeys.append((r, c, is_white))

    if white_king is None:
        return -100000
    if black_king is None:
        return 100000

    for r, c, is_white in serpents:
        pressure = 0

        for dr, dc in KING_DIRS:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue

            target = grid[nr][nc]
            if target in {'.', '*', '#'}:
                continue

            if target.lower() not in NON_POISONABLE:
                if target.isupper() != is_white:
                    pressure += 1  # strong attack
                else:
                    pressure -= 1  # friendly danger

        score += pressure if is_white else -pressure

    for r, c, is_white in beekeepers:
        for dr, dc in KING_DIRS:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue

            target = grid[nr][nc]
            if target in {'.', '*', '#'}:
                continue

            if target.lower() in IMMUNE_TO_SWARM:
                continue

            if target.isupper() != is_white:
                score += 2 if is_white else -2

    def king_safety(r, c, is_white):
        danger = 0

        for dr, dc in KING_DIRS:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue

            piece = grid[nr][nc]

            if piece in {'.', '*', '#'}:
                continue

            if piece.isupper() != is_white:
                danger += 2

            if piece.lower() == 's':
                danger += 4

            if piece.lower() == 'e':
                danger += 5

        return -danger if is_white else danger

    score += king_safety(*white_king, True)
    score += king_safety(*black_king, False)

    for r, c, is_white in joeys:
        count = 0

        for p in grid[r]:
            if p not in {'.', '*', '#'}:
                count += 1

        # about to explode next turn
        if count % 5 == 4:
            blast = 0

            for dr, dc in KING_DIRS + [(0,0)]:
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc):
                    continue

                piece = grid[nr][nc]
                if piece in {'.', '*', '#'}:
                    continue

                val = PIECE_VALUES.get(piece.lower(), 0)

                if piece.isupper() == is_white:
                    blast -= val * 3
                else:
                    blast += val * 3

            score += blast if is_white else -blast

    return score

# =========================
# Helper Functions
# =========================

def is_capture(board_before, board_after):
    return capture_score(board_before, board_after) != 0

def terminal_value(board):
    """Signed game-over value if a king is missing, else None.
    +100000 = White wins (Black king gone), -100000 = Black wins, 0 = both gone.
    Early-exits as soon as both kings are seen."""
    white_king = False
    black_king = False
    for row in board.grid:
        for piece in row:
            if piece == 'K' or piece == 'W':
                white_king = True
            elif piece == 'k' or piece == 'w':
                black_king = True
        if white_king and black_king:
            return None

    if not white_king and not black_king:
        return 0
    # The side whose king is missing has lost. Score is from White's view.
    return -100000 if not white_king else 100000

def is_in_check(board, white=True):
    king_pos = None
    target = 'K' if white else 'k'

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board.grid[r][c] == target:
                king_pos = (r, c)
                break

    if king_pos is None:
        return True  # king gone = checkmate

    enemy_moves = generate_all_moves(board)

    for move in enemy_moves:
        if move.grid[king_pos[0]][king_pos[1]] != target:
            return True

    return False

# =========================
# Minimax
# =========================

def minimax(board, depth, maximizing):
    if depth == 0:
        return evaluate(board) * (1 + 0.01 * depth), None

    moves = generate_all_moves(board)

    if not moves:
        return evaluate(board), None

    best_move = None

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            eval_score, _ = minimax(move, depth - 1, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            eval_score, _ = minimax(move, depth - 1, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move

def move_score(board_before, board_after):
    return evaluate_cached(board_after) - evaluate_cached(board_before)

# =========================
# Alpha-Beta Pruning
# =========================

def alphabeta(board, depth, alpha, beta, maximizing):
    global NODES
    NODES += 1

    if time_is_up():
        raise SearchTimeout

    # Terminal: a king has been captured, stop expanding dead positions.
    term = terminal_value(board)
    if term is not None:
        return term, None

    alpha_orig = alpha
    beta_orig = beta
    key = board_hash(board)

    tt_move = None
    if key in TT:
        tt_depth, tt_value, tt_flag, tt_move = TT[key]

        if tt_depth >= depth:
            if tt_flag == "EXACT":
                return tt_value, tt_move
            elif tt_flag == "LOWER":
                alpha = max(alpha, tt_value)
            elif tt_flag == "UPPER":
                beta = min(beta, tt_value)

            if alpha >= beta:
                return tt_value, tt_move

    if depth <= 0:
        return quiescence(board, depth, alpha, beta, maximizing), None

    moves = generate_all_moves(board)

    if not moves:
        return evaluate_cached(board), None

    # Compute each move's capture gain (mover-relative) exactly once and reuse it for ordering, the LMR test, and capture detection.
    for m in moves:
        m._cap = capture_score(board, m)

    tt_move_hash = board_hash(tt_move) if tt_move is not None else None
    killers = KILLER_MOVES.get(depth, ())

    def move_order(m):
        # Best-for-the-mover first (descending), independent of min/max since the alpha-beta bounds handle the sign; ordering just maximizes cutoffs.
        score = m._cap * 20.0
        if m._cap != 0:
            score += 30000.0
        mh = board_hash(m)
        if tt_move_hash is not None and mh == tt_move_hash:
            score += 1_000_000.0
        if mh in killers:
            score += 40000.0
        return score

    moves.sort(key=move_order, reverse=True)

    best_move = None

    def store_killer(m):
        if m._cap != 0:
            return  # captures are already ordered via their gain
        h = board_hash(m)
        kl = KILLER_MOVES.setdefault(depth, [])
        if h not in kl:
            kl.append(h)
            if len(kl) > 2:
                kl.pop(0)

    if maximizing:
        value = float('-inf')
        for i, move in enumerate(moves):
            new_depth = depth - 1
            # Late Move Reduction: search late quiet moves shallower first, then re-search at full depth only if they look promising.
            reduce = 1 if (depth >= 3 and i >= 4 and move._cap == 0) else 0

            if i == 0:
                score, _ = alphabeta(move, new_depth, alpha, beta, False)
            else:
                score, _ = alphabeta(move, new_depth - reduce, alpha, alpha + 1, False)
                if score > alpha and (reduce or score < beta):
                    score, _ = alphabeta(move, new_depth, alpha, beta, False)

            if score > value:
                value = score
                best_move = move
            if value > alpha:
                alpha = value
            if alpha >= beta:
                store_killer(move)
                break
    else:
        value = float('inf')
        for i, move in enumerate(moves):
            new_depth = depth - 1
            reduce = 1 if (depth >= 3 and i >= 4 and move._cap == 0) else 0

            if i == 0:
                score, _ = alphabeta(move, new_depth, alpha, beta, True)
            else:
                score, _ = alphabeta(move, new_depth - reduce, beta - 1, beta, True)
                if score < beta and (reduce or score > alpha):
                    score, _ = alphabeta(move, new_depth, alpha, beta, True)

            if score < value:
                value = score
                best_move = move
            if value < beta:
                beta = value
            if alpha >= beta:
                store_killer(move)
                break

    if value <= alpha_orig:
        flag = "UPPER"
    elif value >= beta_orig:
        flag = "LOWER"
    else:
        flag = "EXACT"

    TT[key] = (depth, value, flag, best_move)

    return value, best_move

# =========================
# Quiescence
# ========================= 

def quiescence(board, depth, alpha, beta, maximizing):
    global NODES
    NODES += 1

    if time_is_up():
        raise SearchTimeout

    term = terminal_value(board)
    if term is not None:
        return term

    stand_pat = evaluate_cached(board)

    if depth >= MAX_QUIESCENCE_DEPTH:
        return stand_pat

    if maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    # Compute capture gain once per move, keep only captures.
    capture_moves = []
    for m in generate_all_moves(board):
        m._cap = capture_score(board, m)
        if m._cap != 0:
            capture_moves.append(m)

    capture_moves.sort(key=lambda m: m._cap, reverse=True)

    if not capture_moves:
        return stand_pat

    for move in capture_moves:
        score = quiescence(move, depth + 1, alpha, beta, not maximizing)

        if maximizing:
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        else:
            beta = min(beta, score)
            if alpha >= beta:
                break

    return alpha if maximizing else beta

# =========================
# Capture Score
# ========================= 

def capture_score(board_before, board_after):
    before = 0
    after = 0

    gb = board_before.grid
    ga = board_after.grid
    for r in range(BOARD_SIZE):
        rb = gb[r]
        ra = ga[r]
        for c in range(BOARD_SIZE):
            b = rb[c]
            a = ra[c]

            if b not in EMPTY_SQUARES:
                val = PIECE_VALUES.get(b.lower(), 0)
                before += val if b.isupper() else -val

            if a not in EMPTY_SQUARES:
                val = PIECE_VALUES.get(a.lower(), 0)
                after += val if a.isupper() else -val

    return (after - before) * (1 if board_before.turn == 'W' else -1)

# =========================
# Transposition Table and Evaluation Cache
# ========================= 

def board_hash(board):
    # Computed once per finalized board, then cached. Boards are immutable
    # during search (move generation builds a fresh clone per move), so the
    # cached value can never go stale before it is read.
    h = board._hash
    if h is not None:
        return h

    h = 0
    grid = board.grid
    for r in range(BOARD_SIZE):
        row = grid[r]
        for c in range(BOARD_SIZE):
            piece = row[c]
            if piece not in EMPTY_SQUARES:
                h ^= ZOBRIST_TABLE[(r, c, piece)]

    if board.turn == 'W':
        h ^= ZOBRIST_SIDE

    board._hash = h
    return h

def evaluate_cached(board):
    key = board_hash(board)
    if key in EVAL_CACHE:
        return EVAL_CACHE[key]
    
    val = evaluate(board)
    EVAL_CACHE[key] = val
    return val