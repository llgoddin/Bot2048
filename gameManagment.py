
import json
import multiprocessing
import os
import time

from Agent import *
from config import *
from InputOutputFunctions import *
from operations import *


def __run_game(game):
    """Runs a game autonomously using my_algorithm()"""

    while not game['lost']:

        game['move'], game['moveScores'] = my_algorithm(game)

        check_game_lost(game)

        # I changed the order of this loop to record information
        # about the algorithm before the board is moved so
        # in the move log csv the initial board will show scores and
        # a planned move instead of having the scores off by 1
        record_move(game)

        move(game)

    return game


def __find_session_num():
    """Searches recording directory for other sessions and determines next session ID"""

    # figure out number of sessions that have already been recorded
    for (root, dirs, files) in os.walk(CONFIG['recording_path'], topdown=True):
        nextSession = 1

        for d in dirs:
            try:

                if int(d.split('Session')[1]) >= nextSession:
                    nextSession = int(d.split('Session')[1]) + 1

            except ValueError as verr:
                print('Directory ' + str(d) + ' does not end in a number!')

        if nextSession > 99:
            return -1
        return nextSession


def __end_session(session):
    """Creates logs and finishes session"""

    # reset agent and game recording info
    session['recording'] = False
    # gather time information and compile stats
    session['endTime'] = time.time()

    output_logs(session)

    stats = compile_stats(session)

    return stats


def create_game(gameID=0, session=None, path=None):
    """Creates and returns a new game dict"""

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

    gen_tile(game)
    gen_tile(game)

    return game


def create_session(recording=True, totalGames=10):
    """Creates and returns a new session dict"""

    session = {
        'recording': recording,
        'path': None,
        'games': [],
        'startTime': None,
        'endTime': None
    }

    if session['recording']:
        sessionNum = __find_session_num()

        session['path'] = CONFIG['recording_path'] + \
            '/Session' + str(sessionNum)
        os.mkdir(session['path'])
        os.mkdir((session['path'] + str('/MoveLogs')))
        os.mkdir((session['path'] + str('/htmlReportData')))

    session['startTime'] = time.time()

    for i in range(totalGames):
        session['games'].append(create_game(i, session))

    return session


def run_session(s, threads=8):
    """Runs a session of games"""

    if threads > 1:
        p = multiprocessing.Pool(processes=threads)

        results = p.map_async(__run_game, s['games'])

        s['games'] = results.get()

        p.close()
        p.join()

    else:
        for g in s['games']:
            __run_game(g)

    stats = __end_session(s)

    return s['path'], stats
