
from Agent import *
from InputOutputFunctions import *
from operations import *
import multiprocessing
import os
import time

def runGame(game):

    recordMove(game, initialMove=True)

    while not game['lost']:

        game['move'], game['moveScores'] = myAlgorithm(game)

        move(game)

        checkGameLost(game)

        recordMove(game)

    return game


def findSessionNum():

    # figure out number of sessions that have already been recorded
    for (root, dirs, files) in os.walk('/Users/lucasgoddin/Documents/Python Projects/GameRecording', topdown=True):
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

        session['path'] = '/Users/lucasgoddin/Documents/Python Projects/GameRecording/Session' + sessionStr
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
    if threads > 1:
        p = multiprocessing.Pool(processes=threads)

        results = p.map_async(runGame, s['games'])

        s['games'] = results.get()

        p.close()
        p.join()

    else:
        for g in s['games']:
            runGame(g)

    stats = endSession(s)

    return s['path'], stats


def endSession(session):
    # reset agent and game recording info
    session['recording'] = False
    # gather time information and compile stats
    session['endTime'] = time.time()
    

    outputLogs(session)

    stats = compileStats(session)

    

    return stats


def createGame(gameID=0, session=None, path=None):

    game = {
        'id': gameID,
        'board': [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        'move': None,
        'moveLog': None,
        'moveScores': [],
        'score': 0,
        'totalMoves': 0,
        'lost': False
    }

    genTile(game)
    genTile(game)

    return game