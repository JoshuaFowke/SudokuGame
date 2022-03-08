import pygame
import time
import random

pygame.font.init()


class GameBoard:
    board = [
        [0, 5, 2, 7, 0, 0, 9, 0, 0],
        [1, 0, 3, 0, 2, 4, 0, 0, 0],
        [0, 0, 0, 0, 6, 0, 7, 0, 3],
        [3, 0, 0, 0, 5, 0, 0, 9, 7],
        [0, 9, 6, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 0, 4, 0, 0],
        [5, 0, 0, 6, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0]
    ]

    def __init__(self, rows, columns, width, height, surface):
        self.rows = rows
        self.columns = columns
        self.boxes = [[CellValues(self.board[i][j], i, j, width, height) for j in range(columns)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.surface = surface

    def update_model(self):
        self.model = [[self.boxes[i][j].value for j in range(self.columns)] for i in range(self.rows)]

    def place(self, val):
        # attempt to make sketched move permanent
        row, col = self.selected
        if self.boxes[row][col].value == 0:
            self.boxes[row][col].set(val)
            self.update_model()

            if valid_move(self.model, val, (row, col)) and self.solve():
                return True
            else:
                self.boxes[row][col].set(0)
                self.boxes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        # sketch / pencil in move
        row, col = self.selected
        self.boxes[row][col].set_temp(val)

    def draw(self):
        # draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.surface, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(self.surface, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # draw 3 by 3 boxed
        for i in range(self.rows):
            for j in range(self.columns):
                self.boxes[i][j].draw(self.surface)

    def select(self, row, col):
        # reset all other
        for i in range(self.rows):
            for j in range(self.columns):
                self.boxes[i][j].selected = False
        # select a cell
        self.boxes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        # clear a sketched value for a single cell
        row, col = self.selected
        if self.boxes[row][col].value == 0:
            self.boxes[row][col].set_temp(0)

    def clear_all(self):
        # clear all sketched values (required for starting new game)
        for i in range(self.rows):
            for j in range(self.columns):
                self.boxes[i][j].set_temp(0)

    def click(self, pos):
        # recognize a click
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return int(y), int(x)
        else:
            return None

    def is_finished(self):
        # recognize if the board is competed
        for i in range(self.rows):
            for j in range(self.columns):
                if self.boxes[i][j].value == 0:
                    return False
        return True

    def solve(self):
        # solve the board from current state
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid_move(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    def new_game(self):
        # create a new sudoku game and starting clues
        # reset board to empty
        board = [[0 for i in range(9)] for j in range(9)]
        # generate random numbers and seed random row of board.
        raw_num_list1 = list([1, 2, 3, 4, 5, 6, 7, 8, 9])
        raw_num_list2 = list([0, 1, 2, 3, 4, 5, 6, 7, 8])
        random.shuffle(raw_num_list1)
        random.shuffle(raw_num_list2)
        board[raw_num_list2[0]] = raw_num_list1
        # generate solution from seeded board
        self.solve()
        # remove random numbers
        clues_to_remove = 64
        while clues_to_remove > 0:
            random_row = random.randint(0, 8)
            random_col = random.randint(0, 8)
            self.selected = self.boxes[random_row][random_col]
            if self.boxes[random_row][random_col].value == 0:
                continue
            if self.boxes[random_row][random_col].value > 0:
                self.boxes[random_row][random_col].set(0)
                clues_to_remove -= 1

    def solve_gui(self):
        # solve the board on the GUI
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid_move(self.model, i, (row, col)):
                self.model[row][col] = i
                self.boxes[row][col].set(i)
                self.boxes[row][col].draw_change(self.surface, True)
                self.update_model()
                pygame.display.update()

                if self.solve_gui():
                    return True

                self.model[row][col] = 0
                self.boxes[row][col].set(0)
                self.update_model()
                self.boxes[row][col].draw_change(self.surface, False)
                pygame.display.update()

        return False


class CellValues:
    rows = 9
    columns = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, surface):
        # render on GUI
        fnt = pygame.font.SysFont("Arial", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), True, (128, 128, 128))
            surface.blit(text, (x + 5, y + 5))
        elif not (self.value == 0):
            text = fnt.render(str(self.value), True, (0, 0, 0))
            surface.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(surface, (0, 255, 0), (x, y, gap, gap), 3)

    def draw_change(self, surface, g=True):
        # render changes on GUI
        fnt = pygame.font.SysFont("Arial", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(surface, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), True, (0, 0, 0))
        surface.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if g:
            pygame.draw.rect(surface, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(surface, (255, 0, 0), (x, y, gap, gap), 3)

    def set_temp(self, val):
        # set sketched value
        self.temp = val

    def set(self, val):
        # set cell value
        self.value = val


def find_empty(bo):
    # find empty cell values
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return i, j  # row, col

    return None


def valid_move(bo, num, pos):
    # check if the move is valid
    # check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check 3 by 3 box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True


def redraw_window(surface, board, play_time, message):
    # GUI rendering instructions
    surface.fill((255, 255, 255))
    # draw time
    fnt = pygame.font.SysFont("Arial", 40)
    text = fnt.render("Time: " + format_time(play_time), True, (0, 0, 0))
    surface.blit(text, (540 - 200, 560))
    # draw grid and board
    board.draw()
    # draw message
    fnt2 = pygame.font.SysFont("Noteworthy", 40)
    if message == 0:
        text = fnt2.render("Good Luck! ", True, (0, 0, 0))
        surface.blit(text, (40, 550))
    if message == 1:
        text = fnt2.render("Good Move! :) ", True, (0, 255, 0))
        surface.blit(text, (40, 550))
    if message == 2:
        text = fnt2.render("Invalid Move :( ", True, (255, 0, 0))
        surface.blit(text, (40, 550))
    # draw instructions - legend title
    fnt3 = pygame.font.SysFont("Arial", 30, True)
    text = fnt3.render("Legend", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 30))
    fnt4 = pygame.font.SysFont("Arial", 25, False, True)
    text = fnt4.render("Action = Input Key", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 70))
    # draw instructions - legend headers
    fnt5 = pygame.font.SysFont("Arialnarrow", 25)
    text = fnt5.render("Sketch Move  =  Number", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 140))
    text = fnt5.render("Remove Sketch  =  Delete", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 210))
    text = fnt5.render("Try Move  =  Return", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 280))
    text = fnt5.render("Auto Solve  =  Space", True, (0, 0, 0))
    surface.blit(text, (840 - 265, 370))
    fnt6 = pygame.font.SysFont("Arialnarrow", 15)
    text = fnt6.render("Description", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 100))
    # draw instructions - legend descriptions
    text = fnt6.render("Places number non-permanently", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 170))
    text = fnt6.render("Deletes sketched move", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 240))
    text = fnt6.render("Only places value if game is still solvable", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 310))
    text = fnt6.render("Placement is permanent", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 330))
    text = fnt6.render("Solves the rest of the puzzle", True, (0, 0, 0))
    surface.blit(text, (840 - 260, 400))
    # draw 'new game' button with interactive hover
    fnt7 = pygame.font.SysFont("Noteworthy", 25)
    text = fnt7.render("New Game", True, (0, 0, 0))
    surface.blit(text, (580 + 25, 450 + 10))
    mouse = pygame.mouse.get_pos()
    if 580 + 150 > mouse[0] > 580 and 450 + 62 > mouse[1] > 450:
        pygame.draw.rect(surface, (0, 255, 0), (580, 450, 160, 65), 3, 3)
    else:
        pygame.draw.rect(surface, (0, 0, 0), (580, 450, 160, 65), 2, 2)


def format_time(secs):
    # how time is displayed
    sec = secs % 60
    minute = secs // 60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


def play():
    # how the game operates
    surface = pygame.display.set_mode((860, 635), pygame.RESIZABLE)
    pygame.display.set_caption("Sudoku Game")
    board = GameBoard(9, 9, 540, 540, surface)
    key = None
    run = True
    start = time.time()
    message = 0
    while run:

        play_time = round(time.time() - start)
        
        # user inputs and resulting actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    board.solve_gui()

                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.boxes[i][j].temp != 0:
                        if board.place(board.boxes[i][j].temp):
                            message = 1
                        else:
                            message = 2

                        key = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                board_clicked = board.click(pos)
                new_game_button = pygame.Rect((580, 450), (160, 65))
                new_game_clicked = new_game_button.collidepoint(pos)
                if board_clicked:
                    board.select(board_clicked[0], board_clicked[1])
                    key = None
                # button functionality
                if new_game_clicked:
                    if board.is_finished():
                        board.new_game()
                    else:
                        # if game is unsolved auto solve game to avoid infinite loop 
                        board.solve_gui()
                        board.new_game()
                        board.clear_all()

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(surface, board, play_time, message)
        pygame.display.update()


play()
pygame.quit()

