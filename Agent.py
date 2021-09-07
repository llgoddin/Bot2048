import copy

from config import *
import operations


def __corner_check(board):
    """Checks the corners of the board for the largest tile"""

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


def __combo_check(game, verbose=False):
    """Checks the board for potential combinations"""

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


def __map_tile_sizes(game):
    """Returns an ordered dictionary of tiles and locations descending by tile value"""

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


def __check_corner_stacking(game):
    """Checks and scores the largest tiles being next to each other"""

    tileInfo = __map_tile_sizes(game)

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

    score += __compare_tile_coords(largestTiles, secondTiles)

    # test the following to see if it improves sessions
    # score += __compare_tile_coords(largestTiles, thirdTiles)
    score += __compare_tile_coords(secondTiles, thirdTiles)

    return score


def __compare_tile_coords(largerTile, smallerTile):
    """Checks if tiles are stacked next to each other"""

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


def my_algorithm(game, replay=False):
    """Algorithm for autonomously playing 2048"""

    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner

    # The agent uses 4 scores high tile, combo, corner stack and a total of the 3

    # High tile: returns the value of the largest tile being in the corner
    # Combo: weights the value of potential combinations AFTER the move
    # Corner Stack: scores the number of large tiles stacked next to each other
    # Total: sum of the other 3 scores

    moves = [CONFIG['Up'], CONFIG['Left'], CONFIG['Down'], CONFIG['Right']]
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
        comboScore += __combo_check(tempGame)

        operations.move(tempGame, newTile=False)

        highTileScore += __corner_check(tempGame['board'])

        tempScore = 0
        tempHighTileScore = 0
        for nextM in moves:
            tempGame['move'] = nextM

            if tempScore < __combo_check(tempGame):
                tempScore = __combo_check(tempGame)
            # if highTileScore == 0:
            #     GameOperations.move(tempGame, newTile=False)
            #     s = __corner_check(tempGame['board'])
            #     if tempHighTileScore < s:
            #         tempHighTileScore = s
            #     del tempGame
            #     tempGame = copy.deepcopy(filterGame)

        highTileScore += tempHighTileScore

        comboScore += tempScore

        cornerStackScore += __check_corner_stacking(tempGame)

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
    bestMove = CONFIG['Up']
    scoreData = []
    for key, value in moveScoresDict.items():
        if moveScoresDict[bestMove] < value:
            bestMove = key

    scoreData = scoresBreakDown[bestMove]

    del tempGame

    if replay:
        return scoresBreakDown

    return bestMove, scoreData
