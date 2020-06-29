# Lucas Goddin

from Agent import *
from InputOutputFunctions import *
import multiprocessing
import copy
import os
import time
import random


def findSessionNum():

    # figure out number of sessions that have already been recorded
    for (root, dirs, files) in os.walk('/Users/lucasgoddin/Documents/PycharmProjects/GameRecording', topdown=True):
        nextSession = 0

        for d in dirs:
            try:

                if int(d[-2:]) >= nextSession:
                    nextSession = int(d[-2:]) + 1

            except ValueError as verr:
                print('Directory ' + str(d) + ' does not end in a number!')

        if nextSession > 99:
            return -1
        return nextSession


def createSession(recording=True, totalGames=10):
    print('Creating Session...')

    session = {
        'recording': recording,
        'path': None,
        'games': [],
        'startTime': None,
        'endTime': None
    }

    if session['recording']:
        sessionNum = findSessionNum()

        if sessionNum < 10:
            sessionStr = '0' + str(sessionNum)
        elif sessionNum == -1:
            session['recording'] = False
            return session
        else:
            sessionStr = str(sessionNum)

        session['path'] = '/Users/lucasgoddin/Documents/PycharmProjects/GameRecording/Session' + sessionStr
        os.mkdir(session['path'])
        os.mkdir((session['path'] + str('/MoveLogs')))

        stats = open(session['path'] + '/sessionStats.txt', 'w+')
        stats.write('STATS\n')
        stats.write('-' * 10 + '\n')
        stats.close()

        gameSummaries = open(session['path'] + '/gameSummaries.txt', 'w+')
        gameSummaries.write('GAME SUMMARIES\n')
        gameSummaries.write('Game #- Max Tile, Score, Number Of Moves\n')
        gameSummaries.write('-' * 10 + '\n')
        gameSummaries.close()

    session['startTime'] = time.time()

    for i in range(totalGames):
        session['games'].append(createGame(i, session))

    return session


def runSession(s, threads=8):
    if len(s['games']) > 1 and len(s['games']) >= threads:
        p = multiprocessing.Pool(processes=threads)

        results = p.map_async(runGame, s['games'])

        p.close()
        p.join()

        games = results.get()

        for g in games:
            recordGameSummary(g)
    else:
        for g in s['games']:
            runGame(g)
            recordGameSummary(g)

    endSession(s)


def endSession(session):
    print('Ending Session...')
    # reset agent and game recording info
    session['recording'] = False
    # gather time information and compile stats
    session['endTime'] = time.time()

    compileStats(session)


def createGame(gameID, session=None, agent=False):
    game = {
        'id': gameID,
        'logPath': None,
        'board': [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        'move': None,
        'moveHistory': [],
        'newTile': (4, 4),
        'score': 0,
        'agentActive': agent,
        'totalMoves': 0,
        'lost': False
    }

    genTile(game)
    genTile(game)

    if session is not None:
        if session['recording']:
            game['agentActive'] = True
            game['logPath'] = createMoveLog(game, session)

    return game


def combineTiles(board, xDirec, yDirec):
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
                        board[i + (iterator * distance)][j] = 0
                        break
                    elif board[i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif board[i][j + (iterator * distance)] == board[i][j]:
                        board[i][j] *= 2
                        board[i][j + (iterator * distance)] = 0
                        break
                    elif board[i][j + (iterator * distance)] != 0:
                        break


def genTile(game):
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
    if game['move'] is None:
        return None

    boardCopy = copy.deepcopy(game['board'])

    xDirec = 0
    yDirec = 0

    start = 0
    end = 0
    iterator = 0

    # determines which direction tiles should be moving and direction the loop should iterate
    if game['move'] == 'l':
        xDirec = 1
        iterator = 1
    elif game['move'] == 'r':
        xDirec = -1
        iterator = -1
    elif game['move'] == 'u':
        yDirec = 1
        iterator = 1
    else:
        yDirec = -1
        iterator = -1

    if iterator < 0:
        start = 3
        end = 0
    else:
        start = 0
        end = 3

    # combine tiles
    combineTiles(game['board'], xDirec, yDirec)

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
        genTile(game)
        game['totalMoves'] += 1


def checkGameLost(game):
    moves = ['l', 'r', 'u', 'd']
    movesLeft = 4

    for m in moves:
        tempGame = copy.deepcopy(game)

        tempGame['move'] = m

        move(tempGame, False)

        if tempGame['board'] == game['board']:
            movesLeft -= 1

    if movesLeft > 0:
        game['lost'] = False
    else:
        game['lost'] = True


def calculateScore(game):
    s = 0
    for i in range(4):
        for j in range(4):
            s += game['board'][i][j]

    game['score'] = s


def runGame(game):

    recordMove(game, initialMove=True)

    while not game['lost']:

        if game['agentActive']:
            game['move'] = myAlgorithm(game)

        move(game)

        calculateScore(game)

        checkGameLost(game)

        recordMove(game)

    outputMoveLog(game)

    return game
