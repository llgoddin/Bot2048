# Lucas Goddin

# Contains all functions used for...
#   - Recording Games (Input and Output)
#   - Compiling Statistics

from datetime import time
from os import path
from Graphing import *
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import matplotlib.pyplot as plt
import json
import shutil

with open('config.json') as config_file:
    config = json.load(config_file)

def recordMove(game, initialMove=False):

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


def outputLogs(session):
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

        gameSummaries.append([game['id'], maxTile, game['score'], game['totalMoves']])

    df = pd.DataFrame(data=gameSummaries, columns=['Game ID', 'Max Tile', 'Score', 'Total Moves'])
    df.to_csv(session['path'] + '/gameSummaries.csv', index=False)


def compileStats(session):
    summaryData = pd.read_csv(session['path'] + '/gameSummaries.csv')

    statFile = open(session['path'] + '/sessionStats.txt', 'a+')

    maxTile = max(summaryData['Max Tile'])

    df1 = summaryData['Game ID'].where(summaryData['Score'] == max(summaryData['Score']))
    df2 = df1.dropna()

    bestGame = {
        'id': int(df2.iloc[0]),
        'score': summaryData['Score'].max()
    }

    df1 = summaryData['Game ID'].where(summaryData['Score'] == min(summaryData['Score']))
    df2 = df1.dropna()

    worstGame = {
        'id': int(df2.iloc[0]),
        'score': summaryData['Score'].min()
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
    totalTime = computeTotalTime(session['startTime'], session['endTime'])
    avgTime = computeAverageTime(numOfGames, totalTime)

    statFile.write('\nGames in Session:         ' + str(numOfGames) + '\n')
    statFile.write('\nMax Tile:                 ' + str(maxTile))
    statFile.write('\nAverage Score:            ' + str(averageScore))
    statFile.write('\nAverage Max Tile:         ' + str(averageMaxTile))
    statFile.write('\nAverage Number of Moves:  ' + str(averageMoves))
    statFile.write('\n\n4096 Or Higher:           ' + str(percent4096))
    statFile.write('\n2048 Or Higher:           ' + str(percent2048))
    statFile.write('\n1024 Or Higher:           ' + str(percent1024))
    statFile.write('\n512 Or Higher:            ' + str(percent512))
    statFile.write('\n256 Or Higher:            ' + str(percent256))
    statFile.write('\n128 Or Higher:            ' + str(percent128) + '\n')
    statFile.write(
        '\nAverage Game Time:        ' + str(avgTime[0]) + 'h ' + str(avgTime[1]) + 'm ' + str(avgTime[2]) + 's')
    statFile.write(
        '\nTotal Session Time:       ' + str(totalTime[0]) + 'h ' + str(totalTime[1]) + 'm ' + str(totalTime[2]) + 's' + '\n')

    statFile.write('\n\nWorst Game: #' + str(worstGame['id']) + ', Score: ' + str(worstGame['score']))
    statFile.write('\nBest Game: #' + str(bestGame['id']) + ', Score: ' + str(bestGame['score']) + '\n')

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
    

def computeTotalTime(start, end):
    sec = round(end - start)
    (mins, sec) = divmod(sec, 60)
    (hour, mins) = divmod(mins, 60)
    return hour, mins, sec


def computeAverageTime(games, totalTime):
    hoursInSeconds = totalTime[0] * 60 * 60
    minsInSeconds = totalTime[1] * 60

    seconds = totalTime[2] + hoursInSeconds + minsInSeconds
    seconds = seconds / games

    t = computeTotalTime(0, seconds)

    return t


def saveStats(stats):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('statTemplate.html')

    output = template.render(stats=stats)

    with open(config['recording_path'] + '/Session' + stats['ID'] + '/stats.html', 'w') as f:
        f.write(output)

    shutil.copy('./templates/htmlReportData/style.css', config['recording_path'] + '/Session' + stats['ID'] + '/htmlReportData/style.css')


def checkForLog(Session=0, Game=None):
    if path.isdir(config['recording_path'] + '/Session' + str(Session)):
        if Game:
            if path.isfile(config['recording_path'] + '/Session' + str(Session) + '/MoveLogs/game' + str(Game) + 'Log.csv'):
                return True
        else:
            return True
    else:
        return False


def loadReplay(Session=0, Game=0):
    return pd.read_csv(config['recording_path'] + '/Session' + str(Session) + '/MoveLogs/game' + str(Game) + 'Log.csv')


def getReplayBoard(index, data):
    board = []
    row = []

    for i in range(16):
        row.append(data.loc[index, str(i)])

        if len(row) == 4:
            board.append(row)
            row = []
    
    return board
