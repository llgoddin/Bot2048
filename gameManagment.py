
import json
import multiprocessing
import os
import time

from Agent import *
from InputOutputFunctions import *
from operations import *

with open('config.json') as config_file:
    config = json.load(config_file)


def runGame(game):

    while not game['lost']:

        game['move'], game['moveScores'] = myAlgorithm(game)

        checkGameLost(game)

        # I changed the order of this loop to record information
        # about the algorithm before the board is moved so
        # in the move log csv the initial board will show scores and
        # a planned move instead of having the scores off by 1
        recordMove(game)

        move(game)

    return game


def findSessionNum():

    # figure out number of sessions that have already been recorded
    for (root, dirs, files) in os.walk(config['recording_path'], topdown=True):
        nextSession = 0

        for d in dirs:
            try:

                if int(d.split('Session')[1]) >= nextSession:
                    nextSession = int(d.split('Session')[1]) + 1

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

        session['path'] = config['recording_path'] + \
            '/Session' + str(sessionNum)
        os.mkdir(session['path'])
        os.mkdir((session['path'] + str('/MoveLogs')))
        os.mkdir((session['path'] + str('/htmlReportData')))

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
