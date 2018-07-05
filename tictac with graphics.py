import pygame
from pygame.locals import *  # allows recognition of quit and x to quit
import random
import math
import copy
# draft version first pygame July 5 2018
# very messy experimental version

# timer
clock = pygame.time.Clock()

# Set the HEIGHT and WIDTH of the open game window
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 440

ROW_LENGTH = 3  # number of squares in 3x3 grid row
COL_HEIGHT = 3

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (10, 100, 255)
LIGHT_BLUE = (100, 100, 255)
LIGHT_RED = (255, 100, 100)
LIGHT_GREEN = (100, 128, 100)

# load sprites (does not yet show sprites)
x_img = pygame.image.load('x.png')  # x and o are both 60 x 60 px
grey_x_img = pygame.image.load('greyx.png')
o_img = pygame.image.load('o.png')
grey_o_img = pygame.image.load('greyo.png')

# This sets the WIDTH and HEIGHT of each grid location on the hash graphic size
XO_BOARD_IMG_SIZE_X, XO_BOARD_IMG_SIZE_Y = 240, 240  # 240 px square for the 'board' area
SQUARE_WIDTH = XO_BOARD_IMG_SIZE_X/ROW_LENGTH
SQUARE_HEIGHT = XO_BOARD_IMG_SIZE_Y/COL_HEIGHT
SQUARE = int(XO_BOARD_IMG_SIZE_Y/ROW_LENGTH)  # shorter to make it easier

LINE_WIDTH = 10  # line width for hash graphic

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def create_grid():
    grid = [[' ']*3 for _ in range(3)]
    return grid


def space_is_open(grid, row, column):
    if grid[row][column] == ' ':  # is the space empty
        return True
    return False


def draw_xo_board():  # displays the hash graphic
    for line in range(1, ROW_LENGTH):  # create the verticals
        pygame.draw.line(screen, BLACK, (line*SQUARE-.5*LINE_WIDTH, 0),
                         (line*SQUARE-.5*LINE_WIDTH, XO_BOARD_IMG_SIZE_Y), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, line*SQUARE-.5*LINE_WIDTH),
                         (XO_BOARD_IMG_SIZE_X, line*SQUARE-.5*LINE_WIDTH), LINE_WIDTH)


def draw_symbols(grid):  # draw the xs and os
    for index_y, column in enumerate(grid):  # upper-left co-ords of 3x3 grid
        for index_x, row in enumerate(grid):
            if grid[index_y][index_x] == 'X':  # note, yes they are reversed to place graphics!
                screen.blit(x_img, ((index_x * SQUARE)+(.5*LINE_WIDTH),
                                    (index_y * SQUARE)+.5*LINE_WIDTH))
            elif grid[index_y][index_x] == 'O':
                screen.blit(o_img, ((index_x * SQUARE)+(.5*LINE_WIDTH),
                                    (index_y * SQUARE)+.5*LINE_WIDTH))


def draw_intro_buttons():
    #  display a welcome and prompt for symbol choice
    display_text("Welcome!", 0)
    display_text('Click X or O to choose.', 30)

    # below are square buttons to screen, made lighter on mouse over, effect is similar to non commented code
    # pygame.draw.rect(screen, color, (x, y, width, height), line_thickness, 0 for filled) <-comment to remind
    mouse = pygame.mouse.get_pos()
    # if 150 + 65 > mouse[0] > 150 and 310 + 65 > mouse[1] > 310:
    #     pygame.draw.rect(screen, LIGHT_BLUE, (150, 310, 65, 65), 0)
    # else:
    #     pygame.draw.rect(screen, BLUE, (150, 310, 65, 65), 0)
    #
    # if 20 + 65 > mouse[0] > 20 and 310 + 65 > mouse[1] > 310:
    #     pygame.draw.rect(screen, LIGHT_RED, (20, 310, 65, 65), 0)
    # else:
    #     pygame.draw.rect(screen, RED, (20, 310, 65, 65), 0)
    # screen.blit(o_img, (150, 310))
    # screen.blit(x_img, (20, 310))
    if mouse[0] in range(150, 150+65) and mouse[1] in range(310, 310+65):
        screen.blit(grey_o_img, (150, 310))
    else:
        screen.blit(o_img, (150, 310))
    if mouse[0] in range(20, 20+65) and mouse[1] in range(310, 310+65):
        screen.blit(grey_x_img, (20, 310))
    else:
        screen.blit(x_img, (20, 310))


def goes_first():
    players = ['player', 'computer']
    coin_toss = random.choice(players)
    return coin_toss


def draw_who_starts_info(players_symbol, computers_symbol, current_player):
    display_text('You are ' + players_symbol + '.', 0)
    display_text('The computer is ' + computers_symbol + '.', 20)
    display_text('A coin toss decided ', 60)
    if current_player == 'player':
        display_text('you go first.', 80)
    else:
        display_text('the computer goes first.', 80)


def is_win(grid, symbol):  # return True if win for the given board and symbol
    ways_to_win = (
        ((0, 0), (1, 0), (2, 0)),  # col 1
        ((0, 1), (1, 1), (2, 1)),  # col 2
        ((0, 2), (1, 2), (2, 2)),  # col 3
        ((0, 0), (0, 1), (0, 2)),  # row 1
        ((1, 0), (1, 1), (1, 2)),  # row 2
        ((2, 0), (2, 1), (2, 2)),  # row 3
        ((0, 0), (1, 1), (2, 2)),  # diag top left to bottom right
        ((2, 0), (1, 1), (0, 2))   # diag top right to bottom left
        )

    for win in ways_to_win:
        if all(grid[pos_x][pos_y] == symbol for pos_x, pos_y in win):
            return win
    return False

    # for a, b, c in ways_to_win:
    #     if grid[a[0]][a[1]] == grid[b[0]][b[1]] == grid[c[0]][c[1]] == symbol: # <- same thing
    #         return a, b, c,
    # return False


def is_tie(grid):
    for row in grid:
        if ' ' in row:
            return False
    return True


def computers_move(grid, computers_symbol, players_symbol):
    # first check for empty space then see if comp can win by filling it
    grid_copy = copy.deepcopy(grid)
    move_list = [[pos1, pos2] for pos1, row in enumerate(grid) for pos2,
                 item in enumerate(row) if item == ' ']  # list of open moves

    for x, y in move_list:
        grid_copy[x][y] = computers_symbol
        if is_win(grid_copy, computers_symbol):
            grid[x][y] = computers_symbol
            return grid
        else:
            grid_copy[x][y] = ' '

    #  or block if player might win
    for x, y in move_list:
        grid_copy[x][y] = players_symbol
        if is_win(grid_copy, players_symbol):
            grid[x][y] = computers_symbol
            return grid
        else:
            grid_copy[x][y] = ' '

    # or take the center position
    center_y = math.floor(len(grid)/2)
    center_x = len(grid[center_y])//2
    if grid[center_y][center_x] == ' ':
        grid[center_y][center_x] = computers_symbol
        return grid

    # or take an empty corner at random
    corner1 = (0, 0)
    corner2 = (int(len(grid[0])-1), 0)
    corner3 = (0, int(len(grid))-1)
    corner4 = (len(grid)-1, len(grid[len(grid)-1])-1)
    corners = [corner1, corner2, corner3, corner4]
    free_corners = [corner for corner in corners if grid[corner[0]][corner[1]] == ' ']
    if free_corners:
        random_corner = random.choice(free_corners)
        grid[random_corner[0]][random_corner[1]] = computers_symbol
        return grid

    # or pick the next random open space
    random_move = random.choice(move_list)
    grid[random_move[0]][random_move[1]] = computers_symbol
    return grid


def display_text(text_to_display, y_adjust):
    font = pygame.font.SysFont("comicsansms", 20)
    surface_obj = font.render(text_to_display, 1, WHITE)
    screen.blit(surface_obj,
                (120 - surface_obj.get_width() // 2,
                 (260 - surface_obj.get_height() // 2)+y_adjust))


def draw_end_game_screen(current_player, grid, conclusion, win):
    screen.fill(LIGHT_GREEN)    # change screen colour
    draw_xo_board()             # display the board graphic
    draw_symbols(grid)          # display x and os played
    if conclusion == 'win':     # note, win is a tuple of three sets of tuples
        display_text('Winner is ' + current_player + '.', 0)
        # convert win tuples to pixel co-ordinates and draw red line over win
        if win in (((0, 0), (1, 1), (2, 2)),
                   ((2, 0), (1, 1), (0, 2))):  # diagonals
            y1 = (win[0][0] * (SQUARE + (SQUARE//2))-LINE_WIDTH//2)
            x1 = (win[0][1] * (SQUARE + (SQUARE//2))-LINE_WIDTH//2)
            y2 = (win[2][0] * (SQUARE + (SQUARE//2))-LINE_WIDTH//2)
            x2 = (win[2][1] * (SQUARE + (SQUARE//2))-LINE_WIDTH//2)

        elif win in (((0, 0), (0, 1), (0, 2)),  # horizontals
                     ((1, 0), (1, 1), (1, 2)),
                     ((2, 0), (2, 1), (2, 2))):

            y1 = win[0][0] * SQUARE + (SQUARE // 2)
            x1 = win[0][1] * (SQUARE + (SQUARE // 2))
            y2 = win[2][0] * SQUARE + (SQUARE // 2)
            x2 = win[2][1] * (SQUARE + (SQUARE // 2))

        else:
            y1 = win[0][0] * (SQUARE + (SQUARE // 2))  # verticals
            x1 = win[0][1] * SQUARE + (SQUARE // 2)
            y2 = win[2][0] * (SQUARE + (SQUARE // 2))
            x2 = win[2][1] * SQUARE + (SQUARE // 2)

        pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 5)

    elif conclusion == 'tie':
        display_text('It\'s a tie!', 0)

    display_text('Click anywhere to ', 40)
    display_text('start a new game.', 60)


def pause():
    print('before', pygame.time.get_ticks())
    ticks = pygame.time.get_ticks()
    wait = True
    while wait:
        if pygame.time.get_ticks() > ticks + 500:
            wait = False
            print('during', pygame.time.get_ticks())


def main():
    while True:
        # game states
        conclusion = 'none'  # to be used for tied or won
        game_is_in_play = True
        welcome_is_over = False
        player_is_not_done = True
        win = False

        grid = create_grid()
        players_symbol = '_'
        computers_symbol = 'X'
        coin_toss_winner = goes_first()
        current_player = coin_toss_winner

        while player_is_not_done:
            # -----Event Handling-----
            for event in pygame.event.get():
                if event.type == QUIT or (
                     event.type == KEYDOWN and (
                      event.key == K_ESCAPE or
                      event.key == K_q
                     )):
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN and not game_is_in_play:
                    pos = pygame.mouse.get_pos()
                    if pos is not None:
                        player_is_not_done = False  # game is over, restart on mouse click

                if event.type == pygame.MOUSEBUTTONDOWN:  # http://programarcadegames.com/index.php?lang=en&chapter=array_backed_grids
                    pos = pygame.mouse.get_pos()
                    column = pos[0] // SQUARE  # Change the x/y screen coordinates to grid coordinates
                    row = pos[1] // SQUARE  # note this is mouse_x!! not y
                    # print("Click ", pos, "Grid coordinates: ", row, column)
                    if not welcome_is_over:
                        if pos[0] in range(150, 150+65) and pos[1] in range(310, 310+65):
                            players_symbol = 'O'
                        if pos[0] in range(20, 20+65) and pos[1] in range(310, 310+65):
                            players_symbol = 'X'
                            computers_symbol = 'O'
                        if players_symbol in('X', 'O'):
                            welcome_is_over = True

                # -----Game Logic-----
                if welcome_is_over and game_is_in_play:
                    if current_player == 'player' and row < 3 and space_is_open(grid, row, column):
                        grid[row][column] = players_symbol  # Set that array location to player's move
                        win = is_win(grid, players_symbol)  # get the win co-ords so can draw line on win
                        if win:
                            conclusion = 'win'
                            game_is_in_play = False
                        if is_tie(grid):
                            conclusion = 'tie'
                            game_is_in_play = False
                        if game_is_in_play:
                            current_player = 'computer'  # if the move was valid, it is comp's turn

                    if current_player == 'computer':  # note: Do NOT change to elif...
                        grid = computers_move(grid, computers_symbol, players_symbol)
                        win = is_win(grid, computers_symbol)
                        if win:
                            conclusion = 'win'
                            game_is_in_play = False
                        if is_tie(grid):
                            conclusion = 'tie'
                            game_is_in_play = False
                        if game_is_in_play:
                            current_player = 'player'

            # -----Drawing-----
            screen.fill(GREEN)
            draw_xo_board()  # display the board hash graphic

            if game_is_in_play:
                if not welcome_is_over:
                    draw_intro_buttons()
                else:
                    draw_who_starts_info(players_symbol, computers_symbol, coin_toss_winner)
                draw_symbols(grid)  # displays x and os played so far
            if not game_is_in_play:
                draw_end_game_screen(current_player, grid, conclusion, win)

            pygame.display.update()
            clock.tick(60)  # sets fps to 60


main()
