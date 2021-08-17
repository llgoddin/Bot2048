import os
import sys
import math

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
                    output += '│ ' + padLeft + ' ' * len(str(num)) + padRight + ' │ '

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
                setPos(xOrigin + 53, yOrigin + i, ' ' + str(k) + ':  ' + str(v))
            
            i += 1


def setPos(x, y, text=''):
    posStr = "\x1b[%d;%df%s" % (y, x, text)
    print(posStr, end='')


def setPosEx(mem):
    if mem:
        posStr = "\x1b[%d;%df%s" % (mem[1], mem[0], mem[2])
        print(posStr, end='')
    