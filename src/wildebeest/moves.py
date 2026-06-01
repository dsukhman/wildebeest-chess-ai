from .board import *
from .constants import *
from .effects import *
from .utils import *

# =========================
# Main generator
# =========================

def generate_all_moves(board):
    results = []

    for r in range(11):
        for c in range(11):
            piece = board.grid[r][c]

            if not belongs_to_player(piece, board.turn): # If the piece does not belong to the player whose turn it is, skip it and move onto the next iteration.
                continue

            if is_paralyzed(board, r, c): # If the piece is paralyzed by a beekeeper, it cannot move, so skip it.
                continue

            piece_moves = generate_piece_moves(board, r, c)

            for new_board in piece_moves:
                apply_after_effects(new_board)
                new_board.turn = 'B' if board.turn == 'W' else 'W'
                new_board.move_no += 1  
                results.append(new_board)

    return results

def generate_piece_moves(board, r, c):
    piece = board.grid[r][c] # Find current piece

    p = piece.lower()

    # Classic Chess Pieces
    if p == 'p': # Pawn
        return generate_pawn(board, r, c)
    
    if p == 'n': # Knight
        return generate_knight(board, r, c)
    
    if p == 'b': # Bishop
        return generate_slider(board, r, c, BISHOP_DIRS)

    if p == 'r': # Rook
        return generate_slider(board, r, c, ROOK_DIRS)
    
    # Special Pieces (plus king)
    if p == 'k' or p == 'o' or p == 'j': # King or Old Woman or Prince Joey
        return generate_king_like(board, r, c)

    if p == 'w': # King with Jet Pack
        return generate_slider(board, r, c, BISHOP_DIRS)
    
    if p == 's': # Serpent
        return generate_serpent(board, r, c)
    
    if p == 'e': # Empress
       return generate_empress(board, r, c)

    if p == 'c': # Catapult
        return generate_catapult(board, r, c)

    if p == 'g': # Gorilla
        return generate_gorilla(board, r, c)
    
    if p == 'x':  # Golf Cart
        return generate_golf_cart(board, r, c)
    
    if p == 'h': # Time Machine
        return []
    
    if p == 'z': # Beekeeper
        return generate_beekeeper(board, r, c)
    
    print(f"Unknown piece type: {p} at ({r}, {c})")
        
    return []

# =========================
# Pawn
# =========================

def generate_pawn(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Current Piece

    is_white = piece.isupper() # Check if it is on the white team if it is capital with isupper().

    direction = 1 if is_white else -1 # Reverse the direction if it is not on the white team.
    start_row = 1 if is_white else 9 # Set the initial row according to the team.
    promotion_row = 10 if is_white else 0 # Set the promotion row according to the team.

    # Move one spot foward
    nr, nc = r + direction, c 
    if is_walkable(board, nr, nc):
        new_board = board.clone()

        # Check if the pawn is in the promotion row
        new_piece = promote_king_if_needed(piece, board.grid[nr][nc], nr)

        new_board.grid[nr][nc] = new_piece
        new_board.grid[r][c] = underlying_square(r, c)
        results.append(new_board)

        # Move another spot forward if possible
        nr2 = r + 2 * direction
        if r == start_row and is_walkable(board, nr2, nc):
            new_board2 = board.clone()
            new_board2.grid[nr2][nc] = piece
            new_board2.grid[r][c] = underlying_square(r, c)
            results.append(new_board2)

    # Allow pawns to capture pieces diagonally
    for dc in (-1, 1):
        nr, nc = r + direction, c + dc

        if not in_bounds(nr, nc):
            continue

        target = board.grid[nr][nc]
        if not is_enemy(piece, target) or target.lower() == 'g':
            continue
                
        new_board = board.clone()

        # promotion on capture
        new_piece = promote_king_if_needed(piece, board.grid[nr][nc], nr)

        new_board.grid[nr][nc] = new_piece
        new_board.grid[r][c] = underlying_square(r, c)
        results.append(new_board)

    return results

# =========================
# Knight
# =========================

def generate_knight(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in KNIGHT_DIRS: # For each possible knight move
        nr, nc = r + dr, c + dc # Find the new column and row for the knight

        if not in_bounds(nr, nc): # Confirm it is in bounds, otherwise move on to the next iteration.
            continue

        target = board.grid[nr][nc] # Check if there is another piece already on that square.

        if is_friendly(piece, target) or target.lower() == 'g': # Check if the piece on the other square is on the same team, move on to the next iteration if it is.
            continue

        new_board = board.clone() 
        new_board.grid[nr][nc] = piece 
        new_board.grid[r][c] = underlying_square(r, c)

        results.append(new_board)

    return results

# =========================
# Sliding pieces 
# =========================

def generate_slider(board, r, c, directions):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece
    for dr, dc in directions: # Check each possible direction for legal moves
        nr, nc = r + dr, c + dc # Find the new column and row for the piece

        while in_bounds(nr, nc): # Ensure the piece is still in bounds and check for more possible moves
            target = board.grid[nr][nc] # Check if there is a piece already at the location

            if is_friendly(piece, target) or target.lower() == 'g': # If it is a friendly piece, the current piece cannot move past it so break out of the loop
                break

            new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
            new_board.grid[nr][nc] = piece
            new_board.grid[r][c] = underlying_square(r, c)
            results.append(new_board)

            if is_enemy(piece, target): # If it is a enemy piece, break out of the loop and take it.
                break

            nr += dr
            nc += dc

    return results

# =========================
# King-like movement
# (King, Old Woman, Prince Joey)
# =========================

def generate_king_like(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in KING_DIRS:  # Check all legal moves
        nr, nc = r + dr, c + dc # Find the new column and row for the piece

        if not in_bounds(nr, nc): # If it is not in bounds, move onto the next iteration
            continue

        target = board.grid[nr][nc] # Check if there a piece on that square 

        if is_friendly(piece, target) or target.lower() == 'g': # Move to the next iteration if it is a friendly piece 
            continue

        new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
        new_piece = promote_king_if_needed(piece, board.grid[nr][nc]) # If the piece is a king and it moves onto the jet pack, it becomes a king with a jetpack.
            
        new_board.grid[nr][nc] = new_piece

        new_board.grid[r][c] = underlying_square(r, c)

        results.append(new_board)

    return results

def promote_king_if_needed(piece, square, row=None):
    if square == '#':
        if piece == 'K':
            return 'W'
        if piece == 'k':
            return 'w'
    
    if row is not None:
        if piece == 'P' and row == 10:
            return 'H'
        if piece == 'p' and row == 0:
            return 'h'

    return piece

# =========================
# Serpent
# =========================

def generate_serpent(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in KING_DIRS: # Check all legal moves
        nr, nc = r + dr, c + dc # Find the new column and row for the piece

        if not in_bounds(nr, nc): # If it is not in bounds, move onto the next iteration
            continue

        target = board.grid[nr][nc] # Check if there a piece on that square 

        if target not in {'.', '*', '#'}: # The serpent cannot take other pieces nor can it overlap its allies.
            continue

        new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
        new_board.grid[nr][nc] = promote_king_if_needed(piece, board.grid[nr][nc], nr)
        new_board.grid[r][c] = underlying_square(r, c)

        results.append(new_board)

    return results

# =========================
# Empress
# =========================

def generate_empress(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in ROOK_DIRS + BISHOP_DIRS: # Check all legal moves in the rook and bishop  (queen moves)
        nr, nc = r + dr, c + dc

        while in_bounds(nr, nc):
            target = board.grid[nr][nc]

            if is_friendly(piece, target) or target.lower() == 'g': # If it is a friendly piece, the current piece cannot move past it so break out of the loop
                break

            new_board = board.clone()
            new_board.grid[nr][nc] = piece
            new_board.grid[r][c] = underlying_square(r, c)
            results.append(new_board)

            if is_enemy(piece, target):
                break

            nr += dr
            nc += dc

    for dr, dc in KNIGHT_DIRS: # Check all legal knight moves
        nr, nc = r + dr, c + dc

        if not in_bounds(nr, nc):
            continue

        target = board.grid[nr][nc]

        if is_friendly(piece, target):
            continue

        new_board = board.clone()
        new_board.grid[nr][nc] = piece
        new_board.grid[r][c] = underlying_square(r, c)
        results.append(new_board)

    return results

# =========================
# Catapult
# =========================

def generate_catapult(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece
    is_white = piece.isupper() # Check what team the piece is on by checking if it is capital or not

    for dr, dc in KING_DIRS: # Check all legal king-like moves without capture
        nr, nc = r + dr, c + dc # Find the new column and row for the piece

        if not in_bounds(nr, nc): # If it is not in bounds, move onto the next iteration
            continue

        if board.grid[nr][nc] not in {'.', '*', '#'}: # The catapult cannot move like a king if there is a piece in the way, it can only fling it. Move onto the next iteration if there is a piece in the way.
            continue

        new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
        new_board.grid[nr][nc] = piece
        new_board.grid[r][c] = underlying_square(r, c)
        results.append(new_board)

    for dr, dc in KING_DIRS: # Check possible fling moves wthout moving
        ar, ac = r + dr, c + dc  # Find each adjacent piece position
        
        if not in_bounds(ar, ac): # Ensure the adjacent position is in bounds
            continue

        adj_piece = board.grid[ar][ac] # Check if there is a piece to fling

        if not is_friendly(piece, adj_piece): # Confirm it is a friendly piece to fling, move onto the next iteration if it is not
            continue
        
        if adj_piece.lower() in CANNOT_FLING: # If the piece is a time machine, it cannot be flung, so move onto the next iteration.
            continue

        fdr, fdc = -dr, -dc # Calculate the fling direction based on the relative position of the adjacent piece to the catapult

        fr, fc = r + fdr, c + fdc # Calculate the landing position of the flung piece
        
        while in_bounds(fr, fc): # Ensure the landing position is in bounds and check for more possible fling moves in that direction
            landing = board.grid[fr][fc]

            if landing in {'.', '*', '#'}: # If the landing square is empty, the fling is valid and we can add it to the results
                new_board = board.clone()
                new_board.grid[fr][fc] = promote_king_if_needed(adj_piece, board.grid[fr][fc], fr) # Move the flung piece to its landing square
                new_board.grid[ar][ac] = underlying_square(ar, ac)

                results.append(new_board) # Add results but keep checking if we can fling further in that direction

            elif is_enemy(piece, landing): # Check if the spot is an enemy piece, if it is, we may be able to capture it with the fling
                if landing.lower() not in CANNOT_BE_CAPTURED_BY_FLING: # Cannot capture kings or gorillas with the fling, so break out of the loop if it is one of those pieces
                    new_board = board.clone()
                    new_board.grid[fr][fc] = promote_king_if_needed(adj_piece, board.grid[fr][fc], fr) # Move the flung piece to its landing square
                    new_board.grid[ar][ac] = underlying_square(ar, ac)
                    results.append(new_board)

            # else: # Friendly piece blocks the fling, so we cannot fling any further in this direction, so we should break out of the loop
            #    break

            fr += fdr # Move the landing position further in the fling direction to check if we can fling further in that direction
            fc += fdc 

    return results

# =========================
# Gorilla
# =========================

def generate_gorilla(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in KING_DIRS: # Check all legal king-like moves without capture
        nr, nc = r + dr, c + dc # Find the new column and row for the piece

        if not in_bounds(nr, nc): # If it is not in bounds, move onto the next iteration
            continue

        target = board.grid[nr][nc] # Check if there a piece on that square
        
        if target in {'.', '*', '#'}: # If the square is empty, the gorilla can move there like a king
            new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
            new_board.grid[nr][nc] = piece
            new_board.grid[r][c] = underlying_square(r, c)
            results.append(new_board)
            continue # Move onto the next iteration after adding the move if it is an empty square

        # Attempt push
        if target.lower() in CANNOT_PUSH: # Gorilla cannot push another gorilla or hovering piece
            continue

        push_r, push_c = nr + dr, nc + dc # Calculate the position the target piece would be pushed into if the gorilla moves into its square

        if not in_bounds(push_r, push_c): # If the push landing position is out of bounds, the gorilla cannot move in that direction, so move onto the next iteration
            continue

        landing = board.grid[push_r][push_c] # Check what piece is on the landing square for the pushed piece

        if landing.lower() in CANNOT_PUSH_GORILLA: # If the piece being pushed would be pushed into a gorilla, the push is not legal, so move onto the next iteration
            continue

        new_board = board.clone()

        new_board.grid[push_r][push_c] = promote_king_if_needed(target, board.grid[push_r][push_c], push_r) # Move the pushed piece into its landing square
    
        new_board.grid[nr][nc] = piece # Move gorilla into the target square
        new_board.grid[r][c] = underlying_square(r, c) # Replace the gorilla's current square with the proper underlying square

        results.append(new_board)

    return results

# =========================
# Golf Cart
# =========================

def generate_golf_cart(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    if r not in (0, 10): # Golf carts can only move left/right if they are on the top or bottom row, so if they are not, return the empty results
        return results

    for dc in (-1, 1): # Check left and right for possible moves
        nr, nc = r, c + dc # Calculate the new column for the golf cart

        if not in_bounds(nr, nc): # Ensure the new position is in bounds
            continue

        target = board.grid[nr][nc] # Check if there is a piece on the new square

        if is_friendly(piece, target) or target.lower() == 'g': # If it is a friendly piece or a gorilla, the golf cart cannot move there, so move onto the next iteration
            continue

        new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
        new_board.grid[nr][nc] = piece
        new_board.grid[r][c] = underlying_square(r, c)

        results.append(new_board)

    return results

# =========================
# Beekeeper
# =========================

def generate_beekeeper(board, r, c):
    results = [] # Create a new array for possible moves
    piece = board.grid[r][c] # Find the name of the piece

    for dr, dc in KING_DIRS: # Check all adjacent squares for possible paralysis-inducing moves
        nr, nc = r + dr, c + dc # Calculate the new position for the beekeeper to move into

        if not in_bounds(nr, nc): # Ensure the new position is in bounds
            continue

        target = board.grid[nr][nc] # Check if there is a piece on the new square

        if is_friendly(piece, target) or target.lower() == 'g': # If it is a friendly piece or a gorilla, the beekeeper cannot move there, so move onto the next iteration
            continue

        new_board = board.clone() # Clone the board and move the piece while also replacing the current location with the proper underlying square.
        new_board.grid[nr][nc] = piece
        new_board.grid[r][c] = underlying_square(r, c)

        results.append(new_board)

    return results

def is_paralyzed(board, r, c): 

    piece = board.grid[r][c] # Find the piece at the given location
    if piece in {'.', '*', '#'}: # If there is no piece at the location, it cannot be paralyzed
        return False

    if piece.lower() in IMMUNE_TO_SWARM: # Check if piece is immune to swarm paralysis
        return False

    is_white = piece.isupper() # Check what team the piece is on by checking if it is capital or not

    for dr, dc in KING_DIRS: # Check each adjacent square for an enemy beekeeper that would paralyze this piece 
        nr, nc = r + dr, c + dc # Calculate the position of the adjacent square
        if not in_bounds(nr, nc): # Ensure the adjacent position is in bounds
            continue

        neighbor = board.grid[nr][nc] # Check if there is a piece on the adjacent square
        if neighbor in {'.', '*', '#'}: # If there is no piece, it cannot paralyze the piece in question, so move onto the next iteration
            continue

        if neighbor.lower() == 'z' and (neighbor.isupper() != is_white): # If there is an enemy beekeeper adjacent to the piece, it is paralyzed, so we can return True immediately without needing to check the rest of the neighbors.
            return True

    return False
             