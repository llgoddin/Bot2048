import copy

import GameOperations


def determineConserveSpace(game):
    maxTile = 0
    numOfBlanks = 0

    for i in range(4):
        for j in range(4):
            if game['board'][i][j] > maxTile:
                maxTile = game['board'][i][j]
            elif game['board'][i][j] == 0:
                numOfBlanks += 1

    blanksThreshold = 0
    if maxTile >= 512:
        blanksThreshold = 2
    elif maxTile >= 256:
        blanksThreshold = 3
    else:
        blanksThreshold = 4

    if blanksThreshold >= numOfBlanks:
        return True
    return False


def conservationAlg(game):
    moves = ['l', 'r', 'u', 'd']
    moveScoresDict = {}
    tempGame = copy.deepcopy(game)

    for m in moves:
        score = 0
        tempGame['move'] = m
        score += comboCheck(tempGame, conserveMode=True)

        GameOperations.move(tempGame, newTile=False)
        score += cornerCheck(tempGame['board'], conserveMode=True)

        if tempGame['board'] == game['board']:
            moveScoresDict[m] = -1
        else:
            moveScoresDict[m] = score

        tempGame = copy.deepcopy(game)

    return moveScoresDict


def calculateScores(game, currentScore=0, level=0, maxLevel=1):
    moves = ['l', 'r', 'u', 'd']
    moveScoresDict = {}

    tempGame = copy.deepcopy(game)

    for m in moves:
        score = currentScore
        tempGame['move'] = m

        # check combos for immediate move
        score += comboCheck(tempGame)

        GameOperations.move(tempGame, newTile=False)

        score += checkCornerStacking(tempGame)

        score += cornerCheck(tempGame['board'])

        # eliminate moves that don't change the board
        if tempGame['board'] == game['board']:
            score = -1
        elif level < maxLevel:
            score = calculateScores(tempGame, score, level=level + 1, maxLevel=maxLevel)

        # record the move score and reset temp board
        moveScoresDict[m] = score
        tempGame = copy.deepcopy(game)

    if level == 0:
        return moveScoresDict
    else:
        maxScore = 0
        for key, value in moveScoresDict.items():
            if value > maxScore:
                maxScore = value
        return maxScore


def myAlgorithm(game):
    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner

    moveScoresDict = calculateScores(game, currentScore=0, maxLevel=2)

    if game['logPath'] is None:
        print(moveScoresDict)

    # search moveScoresDict for the best move and return it
    bestMove = 'l'
    for key, value in moveScoresDict.items():
        if moveScoresDict[bestMove] < value:
            bestMove = key

    return bestMove


def cornerCheck(board, conserveMode=False):
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
            if conserveMode:
                blankSpaces = 0
                for i in range(4):
                    for j in range(4):
                        if board[i][j] == 0:
                            blankSpaces += 1

                return blankSpaces
            else:
                return largestTile

    return 0


def comboCheck(game, conserveMode=False):
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
                        if conserveMode and game['board'][i][j] != 0:
                            score += 1
                        else:
                            score += 2 * game['board'][i][j]
                        break
                    elif game['board'][i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif game['board'][i][j + (iterator * distance)] == game['board'][i][j]:
                        if conserveMode and game['board'][i][j] != 0:
                            score += 1
                        else:
                            score += 2 * game['board'][i][j]
                        break
                    elif game['board'][i][j + (iterator * distance)] != 0:
                        break

    return score


def mapTileSizes(game):
    tileInfo = {
        'values': [0],
        'locations': []
    }

    for i in range(4):
        for j in range(4):
            for pos in range(len(tileInfo['values'])):
                if game['board'][i][j] > tileInfo['values'][pos]:
                    tileInfo['values'].insert(pos, game['board'][i][j])
                    tileInfo['locations'].insert(pos, [i, j])
                    break

    tileInfo['values'].remove(0)

    return tileInfo


def checkCornerStacking(game):
    tileInfo = mapTileSizes(game)

    score = 0

    for i in range(len(tileInfo['locations']) - 1):

        currentTilePos = tileInfo['locations'][i]
        nextTilePos = tileInfo['locations'][i + 1]

        searches = [[1, 0], [-1, 0], [0, 1], [0, -1]]

        for coordChange in searches:
            nextTilePos = [tileInfo['locations'][i + 1][0] + coordChange[0],
                           tileInfo['locations'][i + 1][1] + coordChange[1]]

            if currentTilePos == nextTilePos:
                score += tileInfo['values'][i + 1] / 2
            else:
                break

        if i > 2:
            break

    return score
