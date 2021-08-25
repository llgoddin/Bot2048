import math
import os
import sys

from Agent import myAlgorithm

SCREENS = {}


def loadScreen(path, memory=None, clear=True):
    if clear:
        os.system('clear')
        setPos(0, 0)

    if path in SCREENS:
        lines = SCREENS[path]['lines']

    else:
        with open(path) as f:
            lines = f.readlines()
            SCREENS[path] = {
                'lines': lines,
                'memory': []
            }

    for l in lines:
        print(l.strip())

    if memory not in SCREENS[path]['memory']:
        SCREENS[path]['memory'].append(memory)

    for m in SCREENS[path]['memory']:
        setPosEx(m)


def getBoardLines(board):
    lines = []

    maxTile = 0
    for line in board:
        for num in line:
            if num > maxTile:
                maxTile = num

    padding = len(str(maxTile)) - 1

    BOARD_WIDTH = 25 + 4 * padding

    boxTop = ' ┌' + '─' * (3 + padding) + '┐'
    boxBottom = ' └' + '─' * (3 + padding) + '┘'
    boxSpacer = '│ ' + ' ' * (padding + 1) + ' │ '

    boardTop = '┌' + '─' * BOARD_WIDTH + '┐'
    boxBottomRow = '│' + boxBottom * 4 + ' │'
    boxTopRow = '│' + boxTop * 4 + ' │'
    boardBottom = '└' + '─' * BOARD_WIDTH + '┘'
    boardSpacer = '│ ' + boxSpacer * 4 + '│'

    lines.append(boardTop)

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


def printBoard(board, replay=False):

    maxTile = 0
    for line in board:
        for num in line:
            if num > maxTile:
                maxTile = num

    if replay:
        x = 40 - (2 * len(str(maxTile)))
    else:
        x = 27 - (2 * len(str(maxTile)))

    if len(str(maxTile)) >= 3:
        y = 10
    else:
        y = 12

    lines = getBoardLines(board)

    for i in range(len(lines)):
        setPos(x, y + i, lines[i])
    setPos(x, y + i + 1)


def printStats(stats):
    i = 1
    xOrigin = 8
    yOrigin = 19

    setPos(8, 10)
    print(" _____             _            _____ _       _       ", end='     ')
    setPos(8, 11)
    print("|   __|___ ___ ___|_|___ ___   |   __| |_ ___| |_ ___ ", end='     ')
    setPos(8, 12)
    print("|__   | -_|_ -|_ -| | . |   |  |__   |  _| .'|  _|_ -|", end='     ')
    setPos(8, 13)
    print("|_____|___|___|___|_|___|_|_|  |_____|_| |__,|_| |___|", end='     ')

    setPos(xOrigin + 51, yOrigin - 1, 'Tile Acheived')
    setPos(xOrigin + 51, yOrigin, '-' * 13)

    for k, v in stats.items():
        if k == 'ID':
            setPos(xOrigin + 60, yOrigin - 6, str(k) + ': ' + str(v))
        elif k == 'Best Game':
            setPos(xOrigin, yOrigin, str(k) + ': ' + str(v))
        elif k == 'Best Score':
            setPos(xOrigin, yOrigin + 2, str(k) + ': ' + str(v))
        elif k == 'Worst Game':
            setPos(xOrigin + 25, yOrigin, str(k) + ': ' + str(v))
        elif k == 'Worst Score':
            setPos(xOrigin + 25, yOrigin + 2, str(k) + ': ' + str(v))
        elif k == 'Max Tile':
            setPos(xOrigin, yOrigin + 4, str(k) + ': ' + str(v))
        elif k == 'Average Max Tile':
            setPos(xOrigin + 25, yOrigin + 4, str(k) + ': ' + str(v))
        elif k == 'Average Score':
            setPos(xOrigin, yOrigin + 6, str(k) + ': ' + str(v))
        elif k == 'Average Moves':
            setPos(xOrigin + 25, yOrigin + 6, str(k) + ': ' + str(v))
        elif k == 'Total Time':
            setPos(xOrigin + 25, yOrigin - 4, str(k) + ': ' + str(v))
        elif k == 'Average Time':
            setPos(xOrigin + 25, yOrigin - 2, str(k) + ': ' + str(v))

        else:
            if len(k) == 4:
                setPos(xOrigin + 53, yOrigin + i, str(k) + ':  ' + str(v))
            else:
                setPos(xOrigin + 53, yOrigin + i,
                       ' ' + str(k) + ':  ' + str(v))

            i += 1


def printReplayData(replayData, sID, gID, moveNum=0):
    setPos(3, 10, '----- Game Info ------')
    setPos(3, 12, '  Session ID: ' + str(sID))
    setPos(3, 13, '     Game ID: ' + str(gID))
    setPos(3, 14, '      Move #: ' + str(moveNum) +
           '/' + str(len(replayData.index) - 1))
    setPos(3, 15, '  Game Score: ' + str(replayData['score'][moveNum]))
    setPos(3, 18, '----- Agent Info -----')
    setPos(3, 20, '   Next Move: ' + str(replayData['move'][moveNum]))
    setPos(3, 21, '  Move Score: ' +
           str(replayData['totalScore'][moveNum]))
    setPos(3, 22, '    Max Tile: ' +
           str(replayData['maxTileScore'][moveNum]))
    setPos(3, 23, '       Combo: ' +
           str(replayData['comboScore'][moveNum]))
    setPos(3, 24, 'Corner Stack: ' +
           str(replayData['cornerStackScore'][moveNum]))


def printMoveData(replayData, sID, gID, moveNum):
    # i generate and print move data at run time to keep saved sessions smaller

    # EX: 1000 Game session storing an extra 3 sets of 4 integers (move data)

    #     1000 games * 900 moves * 12 integers * 4 bytes = 43.2 Million Bytes
    #     43.2 Million Bytes = 43.2 MB

    # I felt adding ~40 MB to each session didn't follow the lightweight theme of Terminal 2048

    board = expandBoard(replayData, moveNum)

    game = {
        'id': 0,
        'move': 'a',
        'board': board
    }

    scoreData = myAlgorithm(game, replay=True)

    # clear graphic board because it will look ugly with the table
    for i in range(10, 29):
        setPos(3 + 22, i, ' '*55)

    # print temp board
    setPos(42, 14, '----- Board -----')
    printTemp(45, 15, board)

    # create table
    xOrigin = 3
    yOrigin = 29

    setPos(xOrigin, yOrigin - 3,
           '--------------------- Move Info ---------------------')
    setPos(xOrigin, yOrigin - 2,
           '  Move  |  Total  |  Max Tile  |  Combo  |  Corner  |')
    setPos(xOrigin, yOrigin - 1,
           '--------|---------|------------|---------|----------|')
    setPos(xOrigin, yOrigin + 0,
           '        |         |            |         |          |')
    setPos(xOrigin, yOrigin + 1,
           '        |         |            |         |          |')
    setPos(xOrigin, yOrigin + 2,
           '        |         |            |         |          |')
    setPos(xOrigin, yOrigin + 3,
           '        |         |            |         |          |')

    # fill table
    i = 0
    for k, v in scoreData.items():
        setPos(xOrigin + 4, yOrigin + i, k)

        setPos(xOrigin + 18 - len(str(v[0])), yOrigin + i, v[0])
        setPos(xOrigin + 31 - len(str(v[1])), yOrigin + i, v[1])
        setPos(xOrigin + 41 - len(str(v[2])), yOrigin + i, v[2])
        setPos(xOrigin + 52 - len(str(v[3])), yOrigin + i, v[3])

        i += 1

    setPos(xOrigin + 55, yOrigin + 2, 'Press Enter')
    setPos(xOrigin + 55, yOrigin + 3, 'To Continue...')


def expandBoard(replayData, moveNum):
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


def printTemp(xOrigin, yOrigin, board):
    x = xOrigin
    y = yOrigin

    for row in board:
        for i in row:
            setPos(x, y, str(i) + ', ')
            x += 2 + len(str(i))
        x = xOrigin
        y += 1


def setPos(x, y, text=''):
    posStr = "\x1b[%d;%df%s" % (y, x, text)
    print(posStr, end='')


def setPosEx(mem):
    if mem:
        posStr = "\x1b[%d;%df%s" % (mem[1], mem[0], mem[2])
        print(posStr, end='')
