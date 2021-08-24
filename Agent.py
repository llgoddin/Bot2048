import copy
import operations


def myAlgorithm(game):
    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner
    moves = ['w', 'a', 's', 'd']
    scoresBreakDown = {}
    moveScoresDict = {}

    for m in moves:
        totalScore = 0
        highTileScore = 0
        comboScore = 0
        cornerStackScore = 0

        filterGame = {
            'id': game['id'],
            'move': game['move'],
            'board': game['board']
        }

        tempGame = copy.deepcopy(filterGame)
        tempGame['move'] = m
        comboScore += comboCheck(tempGame)

        operations.move(tempGame, newTile=False)

        highTileScore += cornerCheck(tempGame['board'])

        tempScore = 0
        tempHighTileScore = 0
        for nextM in moves:
            tempGame['move'] = nextM

            if tempScore < comboCheck(tempGame):
                tempScore = comboCheck(tempGame)
            # if highTileScore == 0:
            #     GameOperations.move(tempGame, newTile=False)
            #     s = cornerCheck(tempGame['board'])
            #     if tempHighTileScore < s:
            #         tempHighTileScore = s
            #     del tempGame
            #     tempGame = copy.deepcopy(filterGame)

        highTileScore += tempHighTileScore

        comboScore += tempScore

        cornerStackScore += checkCornerStacking(tempGame)

        totalScore = highTileScore + comboScore + cornerStackScore

        if tempGame['board'] == filterGame['board']:
            totalScore = -1

        # record the move score and reset temp board
        scoresBreakDown[m] = [totalScore,
                              highTileScore, comboScore, cornerStackScore]
        if totalScore == -1:
            scoresBreakDown[m] = totalScore
        moveScoresDict[m] = totalScore

    # search moveScoresDict for the best move and return it
    bestMove = 'w'
    scoreData = []
    for key, value in moveScoresDict.items():
        if moveScoresDict[bestMove] < value:
            bestMove = key

    scoreData = scoresBreakDown[bestMove]

    del tempGame

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
            return max(64, largestTile)

    return 0


def comboCheck(game, verbose=False):

    filterGame = {
        'move': game['move'],
        'board': game['board']
    }

    tempGame = copy.deepcopy(filterGame)

    score = 0
    xDirec = 0
    yDirec = 0
    iterator = 0
    start = 0
    end = 0
    vert = True

    if tempGame['move'] == 'l':
        xDirec = -1
        vert = False
    elif tempGame['move'] == 'r':
        xDirec = 1
        vert = False
    elif tempGame['move'] == 'u':
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
                    elif tempGame['board'][i + (iterator * distance)][j] == tempGame['board'][i][j] and tempGame['board'][i][j] != 0:
                        if verbose:
                            print(str(tempGame['board'][i + (iterator * distance)][j]) + ' combines with ' + str(
                                tempGame['board'][i][j]) + ' when moved ' + str(tempGame['move']))
                        score += 2 * tempGame['board'][i][j]
                        tempGame['board'][i + (iterator * distance)][j] = 0
                        break
                    elif tempGame['board'][i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif tempGame['board'][i][j + (iterator * distance)] == tempGame['board'][i][j] and tempGame['board'][i][j] != 0:
                        if verbose:
                            print(str(tempGame['board'][i][j + (iterator * distance)]) + ' combines with ' + str(
                                tempGame['board'][i][j]) + ' when moved ' + str(tempGame['move']))
                        score += 2 * tempGame['board'][i][j]
                        tempGame['board'][i][j + (iterator * distance)] = 0
                        break
                    elif tempGame['board'][i][j + (iterator * distance)] != 0:
                        break

    del tempGame
    del filterGame
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

    # if tileInfo['values'][0] > 2047:
    #     print('Game ' + str(game['id']) + ' has reached ' + str(tileInfo['values'][0]))

    return tileInfo


def checkCornerStacking(game):
    tileInfo = mapTileSizes(game)

    largestTiles = {
        'values': [],
        'locations': []
    }
    secondTiles = {
        'values': [],
        'locations': []
    }
    thirdTiles = {
        'values': [],
        'locations': []
    }

    stage = 0
    currentNumStartPos = 0
    for i in range(len(tileInfo['locations']) - 1):
        if tileInfo['values'][i] != tileInfo['values'][currentNumStartPos]:
            stage += 1
            currentNumStartPos = i

        if stage == 0:
            largestTiles['values'].append(tileInfo['values'][i])
            largestTiles['locations'].append(tileInfo['locations'][i])
        elif stage == 1:
            secondTiles['values'].append(tileInfo['values'][i])
            secondTiles['locations'].append(tileInfo['locations'][i])
        elif stage == 2:
            thirdTiles['values'].append(tileInfo['values'][i])
            thirdTiles['locations'].append(tileInfo['locations'][i])

        if stage > 2:
            break

    score = 0

    score += compareTileCoords(largestTiles, secondTiles)
    # added in Session 15
    # score += compareTileCoords(largestTiles, thirdTiles)
    score += compareTileCoords(secondTiles, thirdTiles)

    return score


def compareTileCoords(largerTile, smallerTile):

    searches = [[1, 0], [-1, 0], [0, 1], [0, -1]]

    for coord1 in largerTile['locations']:
        for coord2 in smallerTile['locations']:
            for search in searches:
                newCoord = [coord1[0] + search[0], coord1[1] + search[1]]

                if newCoord == coord2:
                    i = smallerTile['locations'].index(coord2)
                    # Score was divided by 2 up until Session 16
                    score = int(smallerTile['values'][i])
                    return score
    return 0
