# Lucas Goddin

# Contains all functions used for...
#   - Recording Games (Input and Output)
#   - Compiling Statistics

from datetime import time
from Graphing import *
import pandas as pd
import matplotlib.pyplot as plt


def recordMove(game, initialMove=False):

    if game['moveLog'] is None:
        dfColumns = []
        
        for i in range(16):
            dfColumns.append(str(i))
        
        dfColumns.append('score')
        dfColumns.append('move')
        dfColumns.append('totalScore')
        dfColumns.append('maxTileScore')
        dfColumns.append('comboScore')
        dfColumns.append('cornerStackScore')

        game['moveLog'] = pd.DataFrame(columns=dfColumns)


    board = []

    for line in game['board']:
        for tile in line:
            board.append(tile)

    board.append(game['score'])
    board.append(game['move'])

    if initialMove:
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

    stats = {
        'Total Time': str(totalTime[0]) + 'h ' + str(totalTime[1]) + 'm ' + str(totalTime[2]) + 's',
        'Average Time': str(avgTime[0]) + 'h ' + str(avgTime[1]) + 'm ' + str(avgTime[2]) + 's',
        'Max Tile': maxTile,
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


def parseMoveLog(gameNum, sessionNum):
    if gameNum < 10:
        gameStr = '0' + str(gameNum)
    else:
        gameStr = str(gameNum)

    path = '/Users/lucasgoddin/Documents/Python Projects/GameRecording/Session' + str(sessionNum) + \
           '/MoveLogs/moveLogGame' + str(gameStr) + '.txt'

    logFile = open(path, 'r')

    lines = logFile.readlines()[2:]

    moves = []
    boards = []
    currentBoard = []

    for i in range(len(lines)):
        if lines[i][0] == 'I':
            print('Found Initial Board')
            continue
        if lines[i][0] == 'M':
            moves.append(lines[i][-2])

        if lines[i][0] == '-':
            if currentBoard != []:
                boards.append(currentBoard)
                currentBoard = []

        if lines[i][0].isnumeric():
            line = lines[i].split(', ')
            boardLine = []
            for num in line:
                boardLine.append(int(num.split('\n')[0]))
            currentBoard.append(boardLine)

    moves.append('End')

    print(len(moves))
    print(len(boards))
    return moves, boards
