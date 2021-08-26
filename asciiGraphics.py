import math
import os
import sys

from Agent import myAlgorithm

SCREENS = {}


def __get_board_lines(board):
    """Creates ASCII lines of a graphic game board"""

    lines = []

    maxTile = 0
    for line in board:
        for num in line:
            if num > maxTile:
                maxTile = num

    padding = len(str(maxTile)) - 1

    BOARD_WIDTH = 25 + 4 * padding

    # creates graphic tiles
    boxTop = ' ┌' + '─' * (3 + padding) + '┐'
    boxBottom = ' └' + '─' * (3 + padding) + '┘'
    boxSpacer = '│ ' + ' ' * (padding + 1) + ' │ '

    # creates graphic board
    boardTop = '┌' + '─' * BOARD_WIDTH + '┐'
    boxBottomRow = '│' + boxBottom * 4 + ' │'
    boxTopRow = '│' + boxTop * 4 + ' │'
    boardBottom = '└' + '─' * BOARD_WIDTH + '┘'
    boardSpacer = '│ ' + boxSpacer * 4 + '│'

    lines.append(boardTop)

    # renders values into board
    for line in board:

        lines.append(boxTopRow)

        if padding >= 2:
            lines.append(boardSpacer)

        output = '│ '
        for num in line:
            p = padding - (len(str(num)) - 1)
            if p > 0:
                padLeft = ''
                padRight = ''

                if p % 2 == 0:
                    padLeft += ' ' * int(p / 2)
                    padRight += ' ' * int(p / 2)
                else:
                    p = math.floor(p / 2)
                    padLeft += ' ' * p
                    padRight += ' ' * (p + 1)

                if num != 0:
                    output += '│ ' + padLeft + str(num) + padRight + ' │ '
                else:
                    output += '│ ' + padLeft + ' ' * \
                        len(str(num)) + padRight + ' │ '

            else:
                if num != 0:
                    output += '│ ' + str(num) + ' │ '
                else:
                    output += '│   │ '
        output += '│'
        lines.append(output)

        if padding >= 2:
            lines.append(boardSpacer)

        lines.append(boxBottomRow)

    lines.append(boardBottom)

    return lines


def __expand_board(replayData, moveNum):
    """Converts a flat list of board values (1x16), into a two dimensional list (4x4)"""

    input = []
    board = []
    row = []

    for i in range(16):
        input.append(replayData[str(i)][moveNum])

    for i in range(4):
        row = []

        for _ in range(4):
            row.append(input.pop(0))

        board.append(row)
        del row

    return board


def text_out(x, y, text=''):
    """This function uses Colorama's escape sequence to move the cursor and display text"""

    posStr = "\x1b[%d;%df%s" % (y, x, text)
    print(posStr, end='')


def text_out_mem(mem):
    """This function uses Colorama's escape sequence to move the cursor and display previously saved text"""

    if mem:
        posStr = "\x1b[%d;%df%s" % (mem[1], mem[0], mem[2])
        print(posStr, end='')


def load_screen(path, memory=None, clear=True):
    """Load and print screen from .txt file"""

    if clear:
        os.system('clear')
        text_out(0, 0)

    if path in SCREENS:
        lines = SCREENS[path]['lines']

    else:
        with open(path) as f:
            lines = f.readlines()
            SCREENS[path] = {
                'lines': lines,
                'memory': []
            }

    for L in lines:
        print(L.strip())

    # I believe memory functionality is only used once or twice
    # and can be removed easily
    if memory not in SCREENS[path]['memory']:
        SCREENS[path]['memory'].append(memory)

    for m in SCREENS[path]['memory']:
        text_out_mem(m)

        # added extra text out to figure out which screens use memory
        text_out(0, 39, 'This Screen Uses The Screen Memory Feature')


def print_board(board, replay=False, xOrigin=None, yOrigin=None):
    """Prints a graphic game board"""

    maxTile = 0
    for line in board:
        for num in line:
            if num > maxTile:
                maxTile = num

    if xOrigin:
        x = xOrigin
        y = yOrigin

    if replay and xOrigin is None:
        x = 40 - (2 * len(str(maxTile)))
    else:
        x = 27 - (2 * len(str(maxTile)))

    if len(str(maxTile)) >= 3 and yOrigin is None:
        y = 10
    else:
        y = 12

    lines = __get_board_lines(board)

    for i in range(len(lines)):
        text_out(x, y + i, lines[i])
    text_out(x, y + i + 1)


def print_stats(stats):
    """Prints statistics about a session over screen createSession.txt"""

    # use x/y Origin to adjust where on the screen stats are printed
    # use i to iterate through lines of tile data
    i = 1
    xOrigin = 8
    yOrigin = 19

    # over write 'Create Session' with 'Session Stats' once
    # session is complete for cleaner looking UI
    text_out(8, 10, " _____             _            _____ _       _            ")
    text_out(8, 11, "|   __|___ ___ ___|_|___ ___   |   __| |_ ___| |_ ___      ")
    text_out(8, 12, "|__   | -_|_ -|_ -| | . |   |  |__   |  _| .'|  _|_ -|     ")
    text_out(8, 13, "|_____|___|___|___|_|___|_|_|  |_____|_| |__,|_| |___|     ")

    text_out(xOrigin + 51, yOrigin - 1, 'Tile Acheived')
    text_out(xOrigin + 51, yOrigin, '-' * 13)

    for k, v in stats.items():
        if k == 'ID':
            text_out(xOrigin + 60, yOrigin - 6, str(k) + ': ' + str(v))
        elif k == 'Best Game':
            text_out(xOrigin, yOrigin, str(k) + ': ' + str(v))
        elif k == 'Best Score':
            text_out(xOrigin, yOrigin + 2, str(k) + ': ' + str(v))
        elif k == 'Worst Game':
            text_out(xOrigin + 25, yOrigin, str(k) + ': ' + str(v))
        elif k == 'Worst Score':
            text_out(xOrigin + 25, yOrigin + 2, str(k) + ': ' + str(v))
        elif k == 'Max Tile':
            text_out(xOrigin, yOrigin + 4, str(k) + ': ' + str(v))
        elif k == 'Average Max Tile':
            text_out(xOrigin + 25, yOrigin + 4, str(k) + ': ' + str(v))
        elif k == 'Average Score':
            text_out(xOrigin, yOrigin + 6, str(k) + ': ' + str(v))
        elif k == 'Average Moves':
            text_out(xOrigin + 25, yOrigin + 6, str(k) + ': ' + str(v))
        elif k == 'Total Time':
            text_out(xOrigin + 25, yOrigin - 4, str(k) + ': ' + str(v))
        elif k == 'Average Time':
            text_out(xOrigin + 25, yOrigin - 2, str(k) + ': ' + str(v))

        else:
            if len(k) == 4:
                text_out(xOrigin + 53, yOrigin + i, str(k) + ':  ' + str(v))
            else:
                text_out(xOrigin + 53, yOrigin + i,
                         ' ' + str(k) + ':  ' + str(v))

            i += 1


def print_replay_data(replayData, sID, gID, moveNum=0):
    """Prints information about the replay data"""

    text_out(3, 10, '----- Game Info ------')
    text_out(3, 12, '  Session ID: ' + str(sID))
    text_out(3, 13, '     Game ID: ' + str(gID))
    text_out(3, 14, '      Move #: ' + str(moveNum) +
             '/' + str(len(replayData.index) - 1))
    text_out(3, 15, '  Game Score: ' + str(replayData['score'][moveNum]))

    text_out(3, 18, '----- Agent Info -----')
    text_out(3, 20, '   Next Move: ' + str(replayData['move'][moveNum]))
    text_out(3, 21, '  Move Score: ' +
             str(replayData['totalScore'][moveNum]))
    text_out(3, 22, '    Max Tile: ' +
             str(replayData['maxTileScore'][moveNum]))
    text_out(3, 23, '       Combo: ' +
             str(replayData['comboScore'][moveNum]))
    text_out(3, 24, 'Corner Stack: ' +
             str(replayData['cornerStackScore'][moveNum]))


def print_move_data(replayData, sID, gID, moveNum):
    """Prints table detailing Agent.myAlgorithm() move scoring"""

    # i generate and print move data at run time to keep saved sessions smaller

    # EX: 1000 Game session storing an extra 3 sets of 4 integers (move data)

    #     1000 games * 900 moves * 12 integers * 4 bytes = 43.2 Million Bytes
    #     43.2 Million Bytes = 43.2 MB

    # I felt adding ~40 MB to each session didn't follow the lightweight theme of Terminal 2048

    board = __expand_board(replayData, moveNum)

    game = {
        'id': 0,
        'move': 'a',
        'board': board
    }

    scoreData = myAlgorithm(game, replay=True)

    # clear graphic board because it will look ugly with the table
    for i in range(10, 29):
        text_out(3 + 22, i, ' '*55)

    # print smaller board so the following table looks nice
    text_out(42, 14, '----- Board -----')
    print_plain_board(45, 15, board)

    # create table
    xOrigin = 3
    yOrigin = 29

    text_out(xOrigin, yOrigin - 3,
             '--------------------- Move Info ---------------------')
    text_out(xOrigin, yOrigin - 2,
             '  Move  |  Total  |  Max Tile  |  Combo  |  Corner  |')
    text_out(xOrigin, yOrigin - 1,
             '--------|---------|------------|---------|----------|')
    text_out(xOrigin, yOrigin + 0,
             '        |         |            |         |          |')
    text_out(xOrigin, yOrigin + 1,
             '        |         |            |         |          |')
    text_out(xOrigin, yOrigin + 2,
             '        |         |            |         |          |')
    text_out(xOrigin, yOrigin + 3,
             '        |         |            |         |          |')

    # fill table
    i = 0
    for k, v in scoreData.items():
        text_out(xOrigin + 4, yOrigin + i, k)

        text_out(xOrigin + 18 - len(str(v[0])), yOrigin + i, v[0])
        text_out(xOrigin + 31 - len(str(v[1])), yOrigin + i, v[1])
        text_out(xOrigin + 41 - len(str(v[2])), yOrigin + i, v[2])
        text_out(xOrigin + 52 - len(str(v[3])), yOrigin + i, v[3])

        i += 1

    text_out(xOrigin + 55, yOrigin + 2, 'Press Enter')
    text_out(xOrigin + 55, yOrigin + 3, 'To Continue...')


def print_plain_board(xOrigin, yOrigin, board):
    """Prints a game board with minimal graphics"""

    x = xOrigin
    y = yOrigin

    for row in board:
        for i in row:
            text_out(x, y, str(i) + ', ')
            x += 2 + len(str(i))

        x = xOrigin
        y += 1
