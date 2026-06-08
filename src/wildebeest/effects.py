from .constants import *
from .utils import *

# =========================
# After Effects
# =========================

def apply_after_effects(board): # Apply all after effects to the board in the correct order
    handle_cart_return(board)
    serpents = []
    empress = []
    joeys = []
    white_cart = None
    black_cart = None
    tm_white = False
    tm_black = False

    grid = board.grid
    for r in range(11):
        row = grid[r]
        for c in range(11):
            piece = row[c]
            if piece in EMPTY_SQUARES:
                continue
            pl = piece.lower()
            if pl == 's':
                serpents.append((r, c))
            elif pl == 'e':
                empress.append((r, c))
            elif pl == 'j':
                joeys.append((r, c))
            elif piece == 'X':
                white_cart = (r, c)
            elif piece == 'x':
                black_cart = (r, c)
            elif piece == 'H':
                tm_white = True
            elif piece == 'h':
                tm_black = True

    # Serpent poison runs first, so census positions still match the board.
    if serpents or empress:
        handle_serpent_poison(board, serpents, empress)

    # Carts are NON_POISONABLE, so poison did not move them, census carts valid.
    handle_pawn_charge(board, white_cart, black_cart)

    # Time machines only exist after a pawn promotion, skip otherwise.
    if tm_white or tm_black:
        handle_time_machine_charge(board)

    handle_transporters(board)

    if joeys:
        handle_prince_joey(board, joeys)

def handle_cart_return(board):
    new_returns = []

    for r, c in board.cart_returns:
        piece = board.grid[r][c]

        # If the cart was destroyed or moved, ignore it
        if piece not in ('X', 'x'):
            continue

        if piece == 'X':
            board.grid[0][c] = 'X'
        else:
            board.grid[10][c] = 'x'

        board.grid[r][c] = underlying_square(r, c)

    board.cart_returns = new_returns
                
def handle_serpent_poison(board, serpents, empress):
    for r, c in serpents:
        apply_serpent_poison(board, r, c, True)

    for r, c in empress:
        apply_serpent_poison(board, r, c, False)

def apply_serpent_poison(board, sr, sc, is_serpent=True):
    serpent_piece = board.grid[sr][sc] # Find location of serpent
    serpent_is_white = serpent_piece.isupper() # Check what team the serpent is on by checking if it is capital or not
    serpent_is_dead = False
    poisoned_positions = [] # Empty list for spots to poison
    old_woman_positions = [] # Empty list for possible positions of the old woman

    for dr, dc in KING_DIRS: # Check each possible square next to the serpent
        nr, nc = sr + dr, sc + dc # Calculate each position next to the serpent

        if not in_bounds(nr, nc): # Ensure the location is in bounds
            continue

        target = board.grid[nr][nc] # Check if there is a target on that square
        if target in {'.', '*', '#'}:
            continue

        if serpent_is_white == target.isupper(): # Ensure that the target is an enemy and not an ally
            continue

        t = target.lower() 
        if t in NON_POISONABLE: # Check if the target is able to get poisoned, otherwise move on to the next iteration
            continue

        poisoned_positions.append((nr, nc))

    # For each poisoned piece, check if ANY of its neighbors is an opposing Old Woman
    if is_serpent:
        for pr, pc in poisoned_positions:
            for dr, dc in KING_DIRS:
                nr, nc = pr + dr, pc + dc

                if not in_bounds(nr, nc): # Ensure the location is in bounds
                    continue

                neighbor = board.grid[nr][nc] # Check if there is something on that square
                if neighbor in ('.', '*', '#'):
                    continue

                if serpent_is_white == neighbor.isupper(): # Skip if they are on the same team
                    continue

                if neighbor.lower() == 'o' and (nr, nc) not in old_woman_positions: # Add the old woman location
                    old_woman_positions.append((nr, nc))

    # Check if the old woman conversion rule is applicable
    if old_woman_positions and poisoned_positions and is_serpent:
        # Promote each adjacent enemy old woman by checking if they are on the opposite team
        for orow, ocol in old_woman_positions:
            if (orow, ocol) in poisoned_positions:
                continue
            
            board.grid[sr][sc] = underlying_square(sr, sc)  # Remove the serpent from its current position
            serpent_is_dead = True
            
            if serpent_is_white:
                board.grid[orow][ocol] = 'e' 
            else:
                board.grid[orow][ocol] = 'E'

    # Remove poisoned pieces
    if not serpent_is_dead:
        for pr, pc in poisoned_positions:
            board.grid[pr][pc] = underlying_square(pr, pc)
     
def handle_pawn_charge(board, white_cart, black_cart):
    trigger_white = False  # triggers WHITE cart
    trigger_black = False  # triggers BLACK cart

    for c in range(11): # Check the middle row for pawns that would trigger the golf carts
        piece = board.grid[MIDDLE_ROW][c]

        if piece.lower() == 'p': # If there is a pawn in the middle row, it triggers a golf cart.
            if piece.isupper():
                trigger_black = True   # If there is a white pawn, it triggers the black cart
            else:
                trigger_white = True   # If there is a black pawn, it triggers the white cart

    if (trigger_white and trigger_black and
        white_cart and black_cart and
        white_cart[1] == black_cart[1]): # If both carts are triggered and they are in the same column, they sweep simultaneously.

        col = white_cart[1] # Column of the golf carts, which are in the same column
        for r in range(11):
            board.grid[r][col] = underlying_square(r, col)
        return
    
    if trigger_white: # If the white cart is triggered, sweep the column of the white golf cart
        sweep_cart(board, white_cart)

    if trigger_black: # If the black cart is triggered, sweep the column of the black golf cart
        sweep_cart(board, black_cart)

def sweep_cart(board, cart_pos): # Helper function to sweep a column with a golf cart, replacing all pieces in the column with the underlying square and moving the cart to the opposite end of the column
    if cart_pos is None:
        return

    row, col = cart_pos
    
    if row == MIDDLE_ROW:  # cart cannot move
        return
    
    piece = board.grid[row][col]

    if row == 0: # If the cart is at the top of the column, it will move to the bottom after sweeping
        end_row = 10
    else:
        end_row = 0

    for r in range(11): # Replace the piece in the column with the underlying square, removing it from the board. 
        if r == row:
            continue
        board.grid[r][col] = underlying_square(r, col)

    board.grid[end_row][col] = piece # Move the golf cart to the opposite end of the column after sweeping
    board.grid[row][col] = underlying_square(row, col)
    
    board.cart_returns.append((end_row, col))
        
def handle_time_machine_charge(board):
    white_tm_exists = False # Check if there is a white time machine on the board, which would trigger the white golf cart
    black_tm_exists = False # Check if there is a black time machine on the board, which would trigger the black golf cart

    for r in range(11): # Iterate through each row on the board
        for c in range(11): # Iterate through each column on the board
            piece = board.grid[r][c] # Check if there is a time machine on the board
            if piece == 'H':
                white_tm_exists = True 
            elif piece == 'h':
                black_tm_exists = True

    white_cart = None # Position of the white golf cart, if it exists
    black_cart = None # Position of the black golf cart, if it exists

    for r in range(11): # Iterate through each row on the board
        for c in range(11): # Iterate through each column on the board
            piece = board.grid[r][c]
            if piece == 'X':
                white_cart = (r, c)
            elif piece == 'x':
                black_cart = (r, c)
                
    if white_tm_exists: 
        sweep_cart(board, white_cart)

    if black_tm_exists:
        sweep_cart(board, black_cart)
                
def handle_transporters(board):    
    originals = {} # Dictionary to store the original pieces at the transporter positions before rotation
    for r, c in TRANSPORTER_POSITIONS: # Store the original pieces at the transporter positions before rotation
        originals[(r, c)] = board.grid[r][c]

    board.grid[3][1] = originals[(3, 9)] # Move piece from (3, 9) to (3, 1)
    board.grid[7][9] = originals[(3, 1)] # Move piece from (3, 1) to (7, 9)
    board.grid[7][1] = originals[(7, 9)] # Move piece from (7, 9) to (7, 1)
    board.grid[3][9] = originals[(7, 1)] # Move piece from (7, 1) to (3, 9)
    
def handle_prince_joey(board, census_joeys):
    joey_positions = []
    for r, c in census_joeys:
        if (r, c) in TRANSPORTER_POSITIONS:
            continue  # handled by the pad rescan below
        if board.grid[r][c].lower() == 'j':
            joey_positions.append((r, c))

    for r, c in TRANSPORTER_POSITIONS:
        if board.grid[r][c].lower() == 'j':
            joey_positions.append((r, c))

    exploding_joeys = [] # List to store the positions of Prince Joeys that will explode
    for jr, jc in joey_positions: # Iterate through each possible joey location and check if the explosion condition is met
        piece_count = 0 # Count the number of pieces in the same row as Prince Joey
        for col in range(11):
            if board.grid[jr][col] not in {'.', '*', '#'}: # If there is a piece in the same row as Prince Joey, increment the piece count
                piece_count += 1

        if piece_count % 5 == 0: # If the number of pieces in the same row as Prince Joey is divisible by 5, add its position to the list of exploding joeys
            exploding_joeys.append((jr, jc))

    # EXPLODEEEEEEEEEEEEEEEEE
    for jr, jc in exploding_joeys:
        board.grid[jr][jc] = underlying_square(jr, jc) #Remove Prince Joey from the board by replacing it with the underlying square
        for dr, dc in KING_DIRS: # Iterate through the 8 adjacent directions around Prince Joey
            nr, nc = jr + dr, jc + dc
            if in_bounds(nr, nc):
                board.grid[nr][nc] = underlying_square(nr, nc)