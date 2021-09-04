# Lucas Goddin

# Contains all functions used for...
#   - Recording Games (Input and Output)
#   - Compiling Statistics

import json
import shutil
from os import path, walk

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from config import *
from Graphing import *


def record_move(game, initialMove=False):
    """Records data about a move and creates a move log if one is not already there"""

    if game['moveLog'] is None:
        dfColumns = []

        for i in range(16):
            dfColumns.append(str(i))

        dfColumns.append('score')
        dfColumns.append('move')
        dfColumns.append('Win/Loss/Continue')
        dfColumns.append('totalScore')
        dfColumns.append('maxTileScore')
        dfColumns.append('comboScore')
        dfColumns.append('cornerStackScore')

        game['moveLog'] = pd.DataFrame(columns=dfColumns)

    board = []
    winLossContinue = 'c'

    for line in game['board']:
        for tile in line:
            if tile >= 2048:
                winLossContinue = 'w'
            board.append(tile)

    if game['lost']:
        winLossContinue = 'l'

    board.append(game['score'])
    board.append(game['move'])
    board.append(winLossContinue)

    if initialMove or game['lost']:
        for i in range(4):
            board.append(0)
    else:
        for num in game['moveScores']:
            board.append(num)

    game['moveLog'].loc[len(game['moveLog'].index)] = board


def output_logs(session):
    """Saves all data stored using record_move to disk"""

    gameSummaries = []

    for game in session['games']:
        path = session['path'] + '/MoveLogs/game' + str(game['id']) + 'Log.csv'
        if game['moveLog'] is None:
            print('problem outputing game ' + str(game['id']))
        else:
            game['moveLog'].to_csv(path, index=False)

        maxTile = 0

        for row in game['board']:
            if max(row) > maxTile:
                maxTile = max(row)

        gameSummaries.append(
            [game['id'], maxTile, game['score'], game['totalMoves']])

    df = pd.DataFrame(data=gameSummaries, columns=[
                      'Game ID', 'Max Tile', 'Score', 'Total Moves'])
    df.to_csv(session['path'] + '/gameSummaries.csv', index=False)


def compile_stats(session):
    """Compiles stats about a session of games and returns a dictionary of them"""

    summaryData = pd.read_csv(session['path'] + '/gameSummaries.csv')

    maxTile = max(summaryData['Max Tile'])

    df1 = summaryData['Game ID'].where(
        summaryData['Score'] == max(summaryData['Score']))
    df2 = df1.dropna()

    bestGame = {
        'id': int(df2.iloc[0]),
        'score': int(summaryData['Score'].max())
    }

    df1 = summaryData['Game ID'].where(
        summaryData['Score'] == min(summaryData['Score']))
    df2 = df1.dropna()

    worstGame = {
        'id': int(df2.iloc[0]),
        'score': int(summaryData['Score'].min())
    }

    numOfGames = len(summaryData.index)

    percent128 = sum(summaryData['Max Tile'] >= 128) / numOfGames
    percent256 = sum(summaryData['Max Tile'] >= 256) / numOfGames
    percent512 = sum(summaryData['Max Tile'] >= 512) / numOfGames
    percent1024 = sum(summaryData['Max Tile'] >= 1024) / numOfGames
    percent2048 = sum(summaryData['Max Tile'] >= 2048) / numOfGames
    percent4096 = sum(summaryData['Max Tile'] >= 4096) / numOfGames

    averageScore = summaryData['Score'].sum() / numOfGames
    averageMaxTile = summaryData['Max Tile'].sum() / numOfGames
    averageMoves = summaryData['Total Moves'].sum() / numOfGames
    totalTime = __compute_total_timeTime(
        session['startTime'], session['endTime'])
    avgTime = __computer_average_time(numOfGames, totalTime)

    id = session['path'].split('Session')[1]

    stats = {
        'ID': id,

        'Total Time': str(totalTime[0]) + 'h ' + str(totalTime[1]) + 'm ' + str(totalTime[2]) + 's',
        'Average Time': str(avgTime[0]) + 'h ' + str(avgTime[1]) + 'm ' + str(avgTime[2]) + 's',
        'Max Tile': maxTile,
        'Average Max Tile': averageMaxTile,
        'Average Score': averageScore,
        'Average Moves': averageMoves,
        '4096': percent4096,
        '2048': percent2048,
        '1024': percent1024,
        '512': percent512,
        '256': percent256,
        '128': percent128,

        'Worst Game': worstGame['id'],
        'Worst Score': worstGame['score'],

        'Best Game': bestGame['id'],
        'Best Score': bestGame['score']
    }

    return stats


def __compute_total_timeTime(start, end):
    """Computes the total time a session takes"""

    sec = round(end - start)
    (mins, sec) = divmod(sec, 60)
    (hour, mins) = divmod(mins, 60)
    return hour, mins, sec


def __computer_average_time(games, totalTime):
    """Calculates the average time per game in a session"""

    hoursInSeconds = totalTime[0] * 60 * 60
    minsInSeconds = totalTime[1] * 60

    seconds = totalTime[2] + hoursInSeconds + minsInSeconds
    seconds = seconds / games

    t = __compute_total_timeTime(0, seconds)

    return t


def save_stats(stats, new_graph=None):
    """Renders HTML jinja2 template and saves with a copy of style.css and stats.json"""

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('statTemplate.html')

    if new_graph:
        output = template.render(stats=stats, newGraph=new_graph)
    else:
        output = template.render(stats=stats)

    with open(config['recording_path'] + '/Session' + stats['ID'] + '/stats.html', 'w') as f:
        f.write(output)

    shutil.copy('./templates/htmlReportData/style.css',
                config['recording_path'] + '/Session' + stats['ID'] + '/htmlReportData/style.css')

    with open(config['recording_path'] + '/Session' + stats['ID'] + '/htmlReportData/sessionStats.json', 'w') as outfile:
        json.dump(stats, outfile)


def check_for_log(Session=0, Game=None):
    """Checks for the log of a session or game, Returns boolean"""

    if path.isdir(config['recording_path'] + '/Session' + str(Session)):
        if Game:
            if path.isfile(config['recording_path'] + '/Session' + str(Session) + '/MoveLogs/game' + str(Game) + 'Log.csv'):
                return True
        else:
            return True
    else:
        return False


def load_replay(Session=0, Game=0):
    """Loads the replay data of a game"""

    return pd.read_csv(config['recording_path'] + '/Session' + str(Session) + '/MoveLogs/game' + str(Game) + 'Log.csv')


def get_replay_board(index, data):
    """Turns a 1x16 board loaded from replay data into a 4x4 list"""

    board = []
    row = []

    for i in range(16):
        row.append(data.loc[index, str(i)])

        if len(row) == 4:
            board.append(row)
            row = []

    return board


def add_graph(sessionID, gameID):
    """Creates and saves the graph to a game"""

    p = config['recording_path'] + '/Session' + str(sessionID)
    graph_games(gameIDs=[gameID], path=p, names=[
        'Game' + str(gameID) + 'Graph'])

    newGraph = {}
    i = 38

    for (root, dirs, files) in walk(config['recording_path'], topdown=True):
        for f in files:
            if f.startswith('Game') and f.endswith('Graph.png'):
                name = f.split('Graph.png')[0]

                name = name[:4] + ' - ' + name[4:]

                newGraph[name] = str(f)

    stats = None

    with open(config['recording_path'] + '/Session' + str(sessionID) + '/htmlReportData/sessionStats.json') as file:
        stats = json.load(file)

    save_stats(stats, newGraph)
