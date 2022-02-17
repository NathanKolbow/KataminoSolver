import driver
from driver import BOARD_WIDTH, PIECES, valid_five_counts
import numpy as np
from time import time

# TODO:
# - Refactor code so that each offset is evaluated at the same time with NumPy
# - Refactor the code so that there is only ever ONE board in memory
# --> should be relatively easy by at each step, after checking for all zeros:
#     (1) set all values on board to piece_number, then if we get returned to
#     (2a) change all offsets back to 0 simultaneously, otherwise (2b) we won.
# - Multi-threading (LAST)



def solve_boards():
    run_tests = [True, False]

    # Times: | Initial  |  Reduced pivots |
    # - 3:   |  0.00s   |      0.00s      |
    # - 4:   |  0.21s   |      0.12s      |
    # - 5:   |  0.37s   |      0.22s      |
    # - 6:   |  0.52s   |      0.24s      |
    # - 7:   |  8.94s   |      3.73s      |
    # - 8:   |  120.0s  |      41.38s     |
    test = 1
    if run_tests[test-1]:
        piece_sequence = [2, 3, 8, 6, 12, 1, 5, 4]
        for i in range(3, len(piece_sequence)+1):
            driver.BOARD_WIDTH = i
            driver.PIECES = piece_sequence[:i]
            start_time = time()
            result = driver.solve(board=None)
            if result is None:
                print(f'TEST FAILED: solve_board() #{test} (EASY) size {i}')
            print(f'solve_board() #{test} size {i} finished in {time() - start_time:.2f}s.')


    # Times: | Reduced pivots |
    # -  5:  |     0.65s      |
    # -  6:  |     1.05s      |
    # -  7:  |     38.10s     |
    # -  8:  | 974s (FAILED)  |
    # -  9:  |    
    # - 10:  |    
    test += 1
    if run_tests[test-1]:
        piece_sequence = [5, 6, 1, 2, 8, 12, 4, 11, 7, 10]
        for i in range(5, len(piece_sequence)+1):
            driver.BOARD_WIDTH = i
            driver.PIECES = piece_sequence[:i]
            start_time = time()
            result = driver.solve(board=None)
            if result is None:
                print(f'TEST FAILED: solve_board() #{test} (CHALLENGING) size {i}')
            print(f'solve_board() #{test} size {i} finished in {time() - start_time:.2f}s.')

def test_valid_fives():
    driver.BOARD_WIDTH = 3

    test = 1
    board = np.array([[0, 1, 0],
                      [1, 1, 1],
                      [0, 1, 0],
                      [0, 0, 0],
                      [0, 0, 0]])
    result = valid_five_counts(board)
    if result:
        print(f'TEST FAILED: test_valid_fives() #{test}')
    test += 1

    board = np.array([[0, 1, 0],
                      [0, 1, 1],
                      [0, 1, 0],
                      [0, 1, 0],
                      [0, 0, 0]])
    result = valid_five_counts(board)
    if result:
        print(f'TEST FAILED: test_valid_fives() #{test}')
    test += 1

    board = np.array([[0, 0, 0],
                      [0, 1, 1],
                      [0, 1, 0],
                      [0, 1, 0],
                      [0, 1, 0]])
    result = valid_five_counts(board)
    if result:
        print(f'TEST FAILED: test_valid_fives() #{test}')
    test += 1

    board = np.array([[0, 1, 1],
                      [0, 1, 0],
                      [0, 1, 0],
                      [0, 1, 0],
                      [0, 0, 0]])
    result = valid_five_counts(board)
    if not result:
        print(f'TEST FAILED: test_valid_fives() #{test}')
    test += 1

    board = np.array([[6, 0, 0],
                      [6, 0, 0],
                      [6, 6, 0],
                      [6, 0, 0],
                      [0, 0, 0]])
    result = valid_five_counts(board)
    if not result:
        print(f'TEST FAILED: test_valid_fives() #{test}')
    test += 1


if __name__ == '__main__':
    test_valid_fives()
    solve_boards()