# sudoku_solver.py
su1 = [
    [0, 5, 2, 0, 0, 0, 9, 0, 0],
    [1, 0, 3, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 0, 6, 0, 7, 0, 3],
    [3, 0, 0, 0, 5, 0, 0, 0, 7],
    [0, 9, 6, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 8, 0, 0, 4, 0, 0],
    [5, 0, 0, 6, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0]
]


# function to solve a sudoku board using a backtracking algo
def solve(su):
    """
    :param su: 2d list of ints
    :return: solution
    """
    find = find_empty(su)
    if find:
        row, col = find
    else:
        return True

    for i in range(1, 10):
        if valid(su, (row, col), i):
            su[row][col] = i

            if solve(su):
                return True

            su[row][col] = 0

    return False


#  finds empty cell on board
def find_empty(su):
    """
    :param su: partly completed board
    :return: (int, int) row, col
    """

    for i in range(len(su)):
        for j in range(len(su[0])):
            if su[i][j] == 0:
                return i, j  # row, col

    return None


# checks if attempted move us valid
def valid(su, pos, num):
    """
    :param su: 2d list of ints
    :param pos: (row, col)
    :param num: int
    :return: True or False
    """

    # check row
    for i in range(0, len(su)):
        if su[pos[0]][i] == num and pos[1] != 1:
            return False

    # check col
    for i in range(0, len(su)):
        if su[i][pos[1]] == num and pos[1] != i:
            return False

    # check box
    box_hor = pos[1] // 3
    box_vert = pos[0] // 3

    for i in range(box_vert * 3, box_vert * 3 + 3):
        for j in range(box_hor * 3, box_hor * 3 + 3):
            if su[i][j] == num and (i, j) != pos:
                return False

    return True


# print game with added lines to make it easily readable
def print_game(su):
    """
    prints game board
    :param su: 2d list of ints
    :return: none
    """

    for i in range(len(su)):
        if i % 3 == 0 and i != 0:
            print("-----------------------")
        for j in range(len(su[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print((su[i][j]), end="\n")
            else:
                print(str(su[i][j]) + " ", end="")


solve(su1)
print_game(su1)
