# Lucas Goddin

import copy
import random
from operator import xor

from Agent import *


def __combine_tiles(board, xDirec, yDirec):
    """Combines tiles on a board and returns score earned from that turn"""

    scoreEarned = 0
    iterator = 0
    start = 0
    end = 0
    vert = True

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
                    elif board[i + (iterator * distance)][j] == board[i][j]:
                        board[i][j] *= 2
                        scoreEarned += board[i][j]
                        board[i + (iterator * distance)][j] = 0
                        break
                    elif board[i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif board[i][j + (iterator * distance)] == board[i][j]:
                        board[i][j] *= 2
                        scoreEarned += board[i][j]
                        board[i][j + (iterator * distance)] = 0
                        break
                    elif board[i][j + (iterator * distance)] != 0:
                        break

    return scoreEarned


def gen_tile(game):
    """Generates and places a new random tile"""

    newPos = (4, 4)
    r = random.random()
    if r > .9:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)

            if game['board'][i][j] == 0:
                game['board'][i][j] = 4
                success = True
                newPos = (i, j)
    else:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)

            if game['board'][i][j] == 0:
                game['board'][i][j] = 2
                success = True
                newPos = (i, j)
    game['newTile'] = newPos


def move(game, newTile=True):
    """Moves the game board in a given direction"""
    
    if game['move'] is None:
        return None

    boardCopy = copy.deepcopy(game['board'])

    xDirec = 0
    yDirec = 0

    start = 0
    end = 0
    iterator = 0

    # determines which direction tiles should be moving and direction the loop should iterate
    if game['move'] == CONFIG['Left']:
        xDirec = 1
        iterator = 1
    elif game['move'] == CONFIG['Right']:
        xDirec = -1
        iterator = -1
    elif game['move'] == CONFIG['Up']:
        yDirec = 1
        iterator = 1
    elif game['move'] == CONFIG['Down']:
        yDirec = -1
        iterator = -1
    else:
        return None

    if iterator < 0:
        start = 3
        end = 0
    else:
        start = 0
        end = 3

    # combine tiles
    if 'score' in game.keys():
        game['score'] += __combine_tiles(game['board'], xDirec, yDirec)
    else:
        __combine_tiles(game['board'], xDirec, yDirec)

    # compress tiles

    # The problem with this compression code is simple, its ugly. time to try again
    # The addition of cycles works but is extremely sloppy, im going to try to clean it up after debugging carefully
    # I originally thought combination and compression would have to scan the array in opposite directions
    # The commented code below works for opposite directions but the new code will work for the same direction (FIXED)

    for cycles in range(3):
        for i in range(start, end + xDirec, iterator):
            for j in range(start, end + yDirec, iterator):
                if game['board'][i][j] == 0:
                    game['board'][i][j] = game['board'][i + yDirec][j + xDirec]
                    game['board'][i + yDirec][j + xDirec] = 0

    # this was a much harder fix than i anticipated, ill try again later

    # for i in range(start, end + xDirec, iterator):
    #     for j in range(start, end + yDirec, iterator):
    #         if board[i][j] == 0:
    #             for searchDist in range(start, end - (j - xDirec)):
    #                 if board[i + (yDirec * searchDist)][j + (xDirec * searchDist)] != 0:
    #                     board[i][j] = board[i + (yDirec * searchDist)][j + (xDirec * searchDist)]
    #                     board[i + (yDirec * searchDist)][j + (xDirec * searchDist)] = 0
    #                     break

    newPos = (4, 4)
    if boardCopy != game['board'] and newTile:
        gen_tile(game)
        game['totalMoves'] += 1


def check_game_lost(game):
    """Checks a game board for possible moves, returns True if the board can be moved"""

    moves = [CONFIG['Up'], CONFIG['Left'], CONFIG['Down'], CONFIG['Right']]
    movesLeft = 4

    filterGame = {
        'move': game['move'],
        'board': game['board']
    }

    for m in moves:
        tempGame = copy.deepcopy(filterGame)

        tempGame['move'] = m

        move(tempGame, False)

        if tempGame['board'] == game['board']:
            movesLeft -= 1

        del tempGame
    del filterGame

    if movesLeft > 0:
        game['lost'] = False
        return False
    else:
        game['lost'] = True
        return True
