import copy

from Operations import *


def myAlgorithm(game):
    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner

    moves = ['l', 'r', 'u', 'd']
    moveScoresDict = {}

    tempGame = copy.deepcopy(game)

    for m in moves:
        # Used to help weight the ability to get the largest corner back into the corner
        largestInCorner = False
        score = 0
        tempGame['move'] = m

        score += comboCheck(tempGame)

        move(tempGame, newTile=False)

        # calculate score
        tempScore = 0
        for nextM in moves:
            moveScore = comboCheck(tempGame)
            if moveScore > tempScore:
                tempScore = comboCheck(tempGame)

        score += cornerCheck(tempGame['board'])

        if tempGame['board'] == game['board']:
            score = -1

        moveScoresDict[m] = score
        tempGame = copy.deepcopy(game)

    bestMove = 'l'
    for m in moves:
        if moveScoresDict[m] > moveScoresDict[bestMove]:
            bestMove = m

    return bestMove


def cornerCheck(board):
    # find the largest tile
    largestTile = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] > largestTile:
                largestTile = board[i][j]

    # check corners for the largest tile
    cornerCoord = [(0, 0), (0, 3), (3, 0), (3, 3)]

    for corner in cornerCoord:
        if board[corner[0]][corner[1]] == largestTile:
            return largestTile

    return 0


def comboCheck(game):
    score = 0
    xDirec = 0
    yDirec = 0
    iterator = 0
    start = 0
    end = 0
    vert = True

    if game['move'] == 'l':
        xDirec = -1
        vert = False
    elif game['move'] == 'r':
        xDirec = 1
        vert = False
    elif game['move'] == 'u':
        yDirec = -1
    else:
        yDirec = 1

    if not xDirec == 0:
        vert = False

    if xDirec > 0 or yDirec > 0:
        start = 0
        end = 4
        iterator = 1
    else:
        start = 3
        end = -1
        iterator = -1

    for i in range(start, end, iterator):
        for j in range(start, end, iterator):
            # distance searches for values on the board horizontally or vertically from the targeted square
            for distance in range(1, 4):
                if vert:
                    if (i + (iterator * distance)) < 0 or (i + (iterator * distance)) > 3:
                        break
                    elif game['board'][i + (iterator * distance)][j] == game['board'][i][j]:
                        score += 4 * game['board'][i][j]
                        break
                    elif game['board'][i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif game['board'][i][j + (iterator * distance)] == game['board'][i][j]:
                        score += 4 * game['board'][i][j]
                        break
                    elif game['board'][i][j + (iterator * distance)] != 0:
                        break

    return score
