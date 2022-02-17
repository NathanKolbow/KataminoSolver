import sys
from time import sleep
import numpy as np
from time import time
from math import ceil

##############################################
# * Empty square is the pivot point *        #
#                                            #
# Pieces:                                    #
# 1: ▢     2: ▢     3: ▢ ▤   4: ▢            #
#    ▤ ▤      ▤ ▤      ▤        ▤ ▤          #
#      ▤      ▤ ▤      ▤ ▤        ▤ ▤        #
#      ▤                                     #
#                                            #
# 5: ▢ ▤   6: ▢     7:  ▢    8: ▢ ▤          #
#    ▤        ▤ ▤       ▤         ▤ ▤        #
#    ▤        ▤         ▤         ▤          #
#    ▤        ▤         ▤                    #
#                       ▤                    #
#                                            #
# 9: ▢     10: ▢ ▤   11:   ▢    12: ▢ ▤ ▤    #
#    ▤           ▤       ▤ ▤ ▤        ▤      #
#    ▤ ▤ ▤       ▤ ▤       ▤          ▤      #
#                                            #
# Coordinate system numbering:               #
# (0, 0)   (0, 1)   (0, 2)                   #
# (1, 0)   (1, 1)   (1, 2)                   #
# (2, 0)   (2, 1)   (2, 2)                   #
# ...                                        #
##############################################

# TODO: Cut down the search space by not allowing reflections
#       for the first piece, and restricting its board area
#       to half the board
# TODO: Add some heuristics for starting pieces (i.e. 11 should
#       be one of the last pieces placed, because there are so
#       many ways that it can cut the board off, whereas 2 is
#       probably a good starting piece)
# TODO: Optimize the step of searching through potential pivots 
#       by checking ALL offsets at once and removing EVERY
#       pivot that contains that offset.

# Argument 1: board width
# All following arguments: the numbers associated
# which each piece
BOARD_WIDTH = 0
PIECES = []

# Clockwise transformation matrix
CW_TFORM_MAT = np.array([[0, 1], [-1, 0]])

def solve(board=None, pieces=0):
    """
    Brute-force, brain-less, heuristic-less solver. The search space should be small
    enough that we don't actually need to implement any intelligent
    solution methods/heuristics.

    Return:
      List: list of (x, y, piv) tuples corresponding to the (x, y) of the
            pivot point of each piece (in the order given in PIECES) and
            piv: the number of clockwise pivots on the piece, relative to
            its starting position pictured above.
    """
    
    if board is None:
        board = np.zeros((5, BOARD_WIDTH), dtype=int)
    else:
        # Do some checks to make sure that the board is
        # not unsolvable at this point in the search.
        if is_invalid(board):
            return None

    new_piece = PIECES[pieces]
    for x in range(BOARD_WIDTH):
        for y in range(5):
            # If this piece is already taken by another piece, just skip it
            if board[y][x] != 0:
                continue

            piv_range = range(8)

            # Change the pivot range to get rid of repeats
            # Fully symmetric and rotation invariant piece: range(1)
            # Symmetric about one axis: range(4) (skip reflections)
            # Symmetric about both axes: range(2) (skip reflections and all but one rotation)
            # Flip symmetry after 180º: [0, 1, 4, 5]
            if new_piece == 3:
                piv_range = range(4)
            elif new_piece == 7:
                piv_range = range(2)
            elif new_piece == 9:
                piv_range = range(4)
            elif new_piece == 10:
                piv_range = [0, 1, 4, 5]
            elif new_piece == 11:
                piv_range = range(1)
            elif new_piece == 12:
                piv_range = range(4)

            for piv in piv_range:
                new_board = np.copy(board)

                # Grab the offsets that the new peice will fill
                new_piece_filled_offsets = _get_offsets(new_piece, piv)

                # Check if any of the offsets will be invalid
                if y + new_piece_filled_offsets[:, 1].max() >= 5:
                    continue
                elif x + new_piece_filled_offsets[:, 0].max() >= BOARD_WIDTH:
                    continue

                # Go through each space we will fill and check if it
                # is already taken; if it is, skip this step, else
                # continue
                valid = True
                for offset in new_piece_filled_offsets:
                    # # If this offset & pivot goes off the board, it is not valid
                    # if y+offset[1] < 0 or y+offset[1] >= 5 or x+offset[0] < 0 or x+offset[0] >= BOARD_WIDTH:
                    #     valid = False
                    #     continue
                    
                    # # Check if the placement is valid or not
                    if new_board[y+offset[1]][x+offset[0]] != 0:
                        valid = False
                        break
                    # else:
                    new_board[y+offset[1]][x+offset[0]] = new_piece
                
                # Skip ahead if the choice of (x, y) and piv are not valid
                if not valid:
                    continue

                # If we have used all of our pieces, that means that this is a
                # valid solution; return the board. Otherwise, we have not yet
                # used all the pieces, but this is still valid so far; continue
                # to the next piece.
                if pieces == len(PIECES) - 1:
                    return new_board
                else:
                    ans = solve(new_board, pieces+1)
                    
                    # If ans is not None then it is a valid solution, otherwise
                    # we need to keep looking for a solution
                    if ans is not None:
                        return ans

    # This will be reached if the function was run with a beginning board state
    # that contains no solutions
    return None
                

def is_invalid(board):
    """Checks whether a board is guaranteed to be invalid at its given stage

    Args:
        board (np.array): the game board under inspection
    """
    if not valid_five_counts(board.copy()):
        return True

    return False


def valid_five_counts(board):
    """Checks whether there are any isolated sections with a number of spaces which
       is not a multiple of 5.
    """
    # Grab the locations where there are zeros
    zero_y, zero_x = np.where(board == 0)

    # Loop only while we still have valid locations with zeros
    while zero_x.shape != (0, ):
        # Return if we find that the board is invalid
        board[zero_y[0]][zero_x[0]] = -1
        if (1 + valid_five_recur(board, x=zero_x[0], y=zero_y[0])) % 5 != 0:
            return False
        zero_y, zero_x = np.where(board == 0)

    # We're done and haven't found anything wrong, so the board must be valid so far
    return True


def valid_five_recur(board, x=0, y=0):
    """The recursive portion of valid_five_counts

    Args:
        board (np.array): the board
        count (int, optional): Current count. Defaults to 0.
        x (int, optional): Current x-location. Defaults to 0.
        y (int, optional): Current y-location. Defaults to 0.

    Returns:
        _type_: _description_
    """
    total_counted = 0
    if x - 1 >= 0 and board[y][x-1] == 0:
        board[y][x-1] = -1
        total_counted += 1 + valid_five_recur(board, x-1, y)
    if x + 1 < BOARD_WIDTH and board[y][x+1] == 0:
        board[y][x+1] = -1
        total_counted += 1 + valid_five_recur(board, x+1, y)
    if y - 1 >= 0 and board[y-1][x] == 0:
        board[y-1][x] = -1
        total_counted += 1 + valid_five_recur(board, x, y-1)
    if y + 1 < 5 and board[y+1][x] == 0:
        board[y+1][x] = -1
        total_counted += 1 + valid_five_recur(board, x, y+1)

    return total_counted


def _get_offsets(piece_number, pivot):
    """For a given piece_number, returns 5 tuples containing each of the boxes
       that the piece will fill, assuming the piece is placed at (0, 0); i.e.
       the offsets representing the piece's geometry.

    Args:
        piece_number (int): which piece should the offsets be returned for.
    """
    global CW_TFORM_MAT

    if piece_number == 1:
        offsets = np.array([[0, 1, 1, 2, 3], [0, 0, 1, 1, 1]])
    elif piece_number == 2:
        offsets = np.array([[0, 1, 1, 2, 2], [0, 0, 1, 0, 1]])
    elif piece_number == 3:
        offsets = np.array([[0, 0, 1, 2, 2], [0, 1, 0, 0, 1]])
    elif piece_number == 4:
        offsets = np.array([[0, 1, 1, 2, 2], [0, 0, 1, 1, 2]])
    elif piece_number == 5:
        offsets = np.array([[0, 0, 1, 2, 3], [0, 1, 0, 0, 0]])
    elif piece_number == 6:
        offsets = np.array([[0, 1, 1, 2, 3], [0, 0, 1, 0, 0]])
    elif piece_number == 7:
        offsets = np.array([[0, 1, 2, 3, 4], [0, 0, 0, 0, 0]])
    elif piece_number == 8:
        offsets = np.array([[0, 0, 1, 1, 2], [0, 1, 1, 2, 1]])
    elif piece_number == 9:
        offsets = np.array([[0, 1, 2, 2, 2], [0, 0, 0, 1, 2]])
    elif piece_number == 10:
        offsets = np.array([[0, 0, 1, 2, 2], [0, 1, 1, 1, 2]])
    elif piece_number == 11:
        offsets = np.array([[0, 1, 1, 1, 2], [1, 0, 1, 2, 1]])
    elif piece_number == 12:
        offsets = np.array([[0, 0, 0, 1, 2], [0, 1, 2, 1, 1]])
        
    # Clockwise rotations
    for i in range(pivot % 4):
        offsets = np.dot(CW_TFORM_MAT, offsets)

    # Reflection
    if pivot // 4 == 0:
        offsets[1, :] = offsets[1, :].max() - offsets[1, :]

    # Make all offsets positive to help reduce the space that we have to search
    offsets[0, :] = offsets[0, :] - offsets[0, :].min()
    offsets[1, :] = offsets[1, :] - offsets[1, :].min()

    return offsets.transpose()
    

def __revolve_piece(piece_number):
    """Debug function to show all positions a piece can take

    Args:
        piece_number (int): piece number
    """
    piv = 0
    while True:
        board = np.zeros((5, 5), dtype=int)
        offsets = _get_offsets(piece_number, piv)
        for offset in offsets:
            board[offset[1]][offset[0]] = 1
        print_board(board)

        sleep(1)

        piv += 1
        piv = piv % 8


def print_board(board):
    print('\n\n\n\n')
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            print(board[j][i], end=' ')
        print(end='\n')


if __name__ == '__main__':
    try:
        BOARD_WIDTH = int(sys.argv[1])
    except:
        print('Board width must be an integer.')
        sys.exit(1)

    if BOARD_WIDTH < 3:
        print('Board width must be >= 3.')
        sys.exit(2)

    if len(sys.argv) != BOARD_WIDTH + 2:
        print('Number of pieces input must be equal to the width of the board.')
        sys.exit(3)

    PIECES = np.array([int(arg) for arg in sys.argv[2:]])

    # Now run recursive solver
    start_sec = time()

    ans = solve()
    print(ans)

    print(f'Solution found in {time()-start_sec:.2f} seconds.')