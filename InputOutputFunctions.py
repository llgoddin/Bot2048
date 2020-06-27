# Lucas Goddin

import os
import time


def printBoard(board):
    # prints board values to console
    print('-' * 11)
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end=', ')
        print()


def readBoard():
    boardFile = open('Board.txt', 'r')
    board = boardFile.read()

    # splits rows by \n and elements in rows by ,
    boardLines = board.split('\n')
    boardArray = []
    for line in boardLines:
        boardArray.append(line.split(','))

    # changes boardArray values from char to int
    for i in range(0, 4):
        for j in range(0, 4):
            boardArray[i][j] = int(boardArray[i][j])

    boardFile.close()

    return boardArray


def writeBoard(board):
    boardFile = open('Board.txt', 'w')

    # Writes the board with correct formatting to Board.txt
    for i in range(0, 4):
        for j in range(0, 4):
            if j < 3:
                boardFile.write(str(board[i][j]) + ',')
            else:
                boardFile.write(str(board[i][j]))
        if i < 3:
            boardFile.write('\n')

    boardFile.close()


def createMoveLog(game, session):
    if game['id'] < 10:
        numStr = '0' + str(game['id'])
    else:
        numStr = str(game['id'])

    logPath = session['path'] + '/MoveLogs/moveLogGame' + numStr + '.txt'

    moveLog = open(logPath, 'w+')
    moveLog.write('START MOVE LOG\n')
    moveLog.write('-' * 10 + '\n')

    moveLog.close()

    return logPath


def recordMove(game, initialMove=False):
    if game['logPath'] is None:
        return None

    boardStr = ''

    for i in range(4):
        for j in range(4):
            if j < 3:
                boardStr += str(game['board'][i][j]) + ', '
            else:
                boardStr += str(game['board'][i][j])
        boardStr += '|'

    if initialMove:
        move = ('INITIAL MOVE\n', None, boardStr)
    else:
        move = (game['totalMoves'], game['move'], boardStr)

    game['moveHistory'].append(move)


def recordGameSummary(game):
    if game['logPath'] is None:
        return None

    # find the biggest tile
    maxTile = 0
    for i in range(4):
        for j in range(4):
            if game['board'][i][j] > maxTile:
                maxTile = game['board'][i][j]

    gameSummariesPath = game['logPath'].split('/MoveLogs')[0]

    gameSumFile = open((gameSummariesPath + '/gameSummaries.txt'), 'a+')

    gameSumFile.write('Game ' + str(game['id']) + '- ' + str(maxTile) + ', ' + str(game['score']) + ', ' + str(game['totalMoves']) + '\n')

    gameSumFile.close()


def outputMoveLog(game):
    if game['logPath'] is None:
        return None

    print('Saving Game ' + str(game['id']) + ' Move Log')

    moveLog = open(game['logPath'], 'a+')

    for moves in game['moveHistory']:
        if moves[0] == 'INITIAL MOVE\n':
            moveLog.write(moves[0])
        else:
            moveLog.write('MOVE ' + str(moves[0]) + ': ' + str(moves[1]) + '\n')
        moveLog.write('-' * 10 + '\n')

        boardLines = str(moves[2]).split('|')

        for line in boardLines:
            if line != boardLines[len(boardLines) - 1]:
                moveLog.write(line + '\n')
            else:
                moveLog.write(line)

        moveLog.write('-' * 10 + '\n')
        moveLog.write('\n')

    moveLog.close()

    del game['moveHistory']


def compileStats(session):
    gameSummaries = open((session['path'] + '/gameSummaries.txt'), 'r')

    lines = gameSummaries.readlines()

    gameSummaries.close()

    statFile = open(session['path'] + '/sessionStats.txt', 'a+')

    maxTile = 0

    bestGame = {
        'id': 0,
        'score': 0
    }

    worstGame = {
        'id': 0,
        'score': 10000
    }

    totalMaxTile = 0
    totalScore = 0
    totalMoveNumber = 0

    num4096 = 0
    num2048 = 0
    num1024 = 0
    num512 = 0
    num256 = 0
    num128 = 0

    numOfGames = len(session['games'])

    for l in lines[3:]:
        statString = l.split('-')
        stats = statString[1].split(', ')

        for s in stats:
            s = s.strip()

        if int(stats[1]) < worstGame['score']:
            worstGame['score'] = int(stats[1])
            worstGame['id'] = statString[0][-2:]

        if int(stats[1]) > bestGame['score']:
            bestGame['score'] = int(stats[1])
            bestGame['id'] = statString[0][-2:]

        totalMaxTile += int(stats[0])
        totalScore += int(stats[1])
        totalMoveNumber += int(stats[2])

        if int(stats[0]) >= maxTile:
            maxTile = int(stats[0])

        if int(stats[0]) >= 128:
            num128 += 1
        if int(stats[0]) >= 256:
            num256 += 1
        if int(stats[0]) >= 512:
            num512 += 1
        if int(stats[0]) >= 1024:
            num1024 += 1
        if int(stats[0]) >= 2048:
            num2048 += 1
        if int(stats[0]) >= 4096:
            num4096 += 1

    percent128 = num128 / numOfGames
    percent256 = num256 / numOfGames
    percent512 = num512 / numOfGames
    percent1024 = num1024 / numOfGames
    percent2048 = num2048 / numOfGames
    percent4096 = num4096 / numOfGames

    averageScore = totalScore / numOfGames
    averageMaxTile = totalMaxTile / numOfGames
    averageMoves = totalMoveNumber / numOfGames
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

    print('Session Complete!')
    print('Find stats in dir ' + str(session['path']))


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
