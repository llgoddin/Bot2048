import copy

import GameOperations


def myAlgorithm(game):
    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner
    moves = ['l', 'r', 'u', 'd']
    scoresBreakDown = {}
    moveScoresDict = {}

    for m in moves:
        totalScore = 0
        highTileScore = 0
        comboScore = 0
        cornerStackScore = 0

        tempGame = copy.deepcopy(game)
        tempGame['move'] = m
        comboScore += comboCheck(tempGame)

        GameOperations.move(tempGame, newTile=False)

        tempScore = 0
        for nextM in moves:
            tempGame['move'] = nextM
            if tempGame['logPath'] is None:
                print(str(m) + ' then ' + str(nextM) + ' produces ' + str(comboCheck(tempGame, verbose=True)))
            if tempScore < comboCheck(tempGame):
                tempScore = comboCheck(tempGame)
        comboScore += tempScore

        cornerStackScore += checkCornerStacking(tempGame)
        highTileScore += cornerCheck(tempGame['board'])

        totalScore = highTileScore + comboScore + cornerStackScore

        if tempGame['board'] == game['board']:
            totalScore = -1

        # record the move score and reset temp board
        scoresBreakDown[m] = [totalScore, highTileScore, comboScore, cornerStackScore]
        if totalScore == -1:
            scoresBreakDown[m] = totalScore
        moveScoresDict[m] = totalScore

    # search moveScoresDict for the best move and return it
    bestMove = 'l'
    scoreData = []
    for key, value in moveScoresDict.items():
        if moveScoresDict[bestMove] < value:
            bestMove = key

    scoreData = scoresBreakDown[bestMove]
    if game['logPath'] is None:
        print(moveScoresDict)
        print(scoresBreakDown)
        print('Alg Chose move ' + str(bestMove))
        print('Score Breakdown: ' + str(scoreData))

    return bestMove, scoreData


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


def comboCheck(game, verbose=False):

    game = copy.deepcopy(game)

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
                    elif game['board'][i + (iterator * distance)][j] == game['board'][i][j] and game['board'][i][j] != 0:
                        if verbose:
                            print(str(game['board'][i + (iterator * distance)][j]) + ' combines with ' + str(game['board'][i][j]) + ' when moved ' + str(game['move']))
                        score += 2 * game['board'][i][j]
                        game['board'][i + (iterator * distance)][j] = 0
                        break
                    elif game['board'][i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif game['board'][i][j + (iterator * distance)] == game['board'][i][j] and game['board'][i][j] != 0:
                        if verbose:
                            print(str(game['board'][i][j + (iterator * distance)]) + ' combines with ' + str(game['board'][i][j]) + ' when moved ' + str(game['move']))
                        score += 2 * game['board'][i][j]
                        game['board'][i][j + (iterator * distance)] = 0
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
                break

        if i > 2:
            break

    return score
