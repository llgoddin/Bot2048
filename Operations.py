# Lucas Goddin
# June 12, 2020
# Operations used by 2048 game and agents

import copy
import os
import random
import time


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


def createMoveLog(num, path):
    if num < 10:
        numStr = '0' + str(num)
    else:
        numStr = str(num)
    moveLog = open(path + '/MoveLogs/moveLogGame' + numStr + '.txt', 'w+')
    moveLog.write('START MOVE LOG\n')
    moveLog.write('-' * 10 + '\n')
    moveLog.close()


def createSession(recording=True, totalGames=10):
    print('Creating Session...')

    session = {
        'recording': recording,
        'path': None,
        'totalGames': totalGames,
        'gamesCompleted': 0,
        'game': None,
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
    session['game'] = createGame(session)

    return session


def endSession(session):
    print('Ending Session...')
    # reset agent and game recording info
    session['recording'] = False
    session['game']['agentActive'] = False
    session['gamesCompleted'] = 0
    # gather time information and compile stats
    session['endTime'] = time.time()
    t = computeTotalTime(session['startTime'], session['endTime'])
    compileStats(t, session['path'])


def recordMove(session, initialMove=False):
    # TODO
    # work on making this more intuitive and add game over line
    # add initial board write

    if not session['recording']:
        return None

    if session['gamesCompleted'] < 10:
        gameNumStr = '0' + str(session['gamesCompleted'])
    else:
        gameNumStr = str(session['gamesCompleted'])

    moveLog = open((str(session['path']) + '/MoveLogs/moveLogGame' + gameNumStr + '.txt'), 'a+')

    if initialMove:
        moveLog.write('INITIAL BOARD\n')
    else:
        moveLog.write('MOVE ' + str(session['game']['totalMoves']) + ': ' + str(session['game']['move']) + '\n')
    moveLog.write('-' * 10 + '\n')

    for i in range(4):
        for j in range(4):
            if j < 3:
                moveLog.write(str(session['game']['board'][i][j]) + ', ')
            else:
                moveLog.write(str(session['game']['board'][i][j]))

        moveLog.write('\n')
    moveLog.write('-' * 10 + '\n')
    moveLog.write('\n')
    moveLog.close()


def recordGameSummary(session):
    if not session['recording']:
        return None

    print('Recording Game ' + str(session['gamesCompleted']))
    maxTile = 0
    for i in range(4):
        for j in range(4):
            if session['game']['board'][i][j] > maxTile:
                maxTile = session['game']['board'][i][j]

    gameSumFile = open((str(session['path']) + '/gameSummaries.txt'), 'a+')

    gameSumFile.write('Game ' + str(session['gamesCompleted']) + '- ' + str(maxTile) + ', ' + str(session['game']['score']) + ', ' + str(session['game']['totalMoves']) + '\n')

    gameSumFile.close()

    session['gamesCompleted'] += 1

    if session['gamesCompleted'] < session['totalGames']:
        session['game'] = createGame(session)

    else:
        endSession(session)


def compileStats(timer, path):
    sessionNum = findSessionNum() - 1
    gameSummaries = open((path + '/gameSummaries.txt'), 'r')

    lines = gameSummaries.readlines()

    gameSummaries.close()

    statFile = open(path + '/sessionStats.txt', 'a+')

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

    numOfGames = len(lines) - 3

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
    avgTime = computeAverageTime(numOfGames, timer)

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
        '\nTotal Session Time:       ' + str(timer[0]) + 'h ' + str(timer[1]) + 'm ' + str(timer[2]) + 's' + '\n')

    statFile.write('\n\nWorst Game: #' + str(worstGame['id']) + ', Score: ' + str(worstGame['score']))
    statFile.write('\nBest Game: #' + str(bestGame['id']) + ', Score: ' + str(bestGame['score']) + '\n')

    print('Session Complete!')
    print('Find stats in dir ' + str(path))


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


def printBoard(board):
    # prints board values to console
    print('-' * 11)
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end=', ')
        print()


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


def createGame(session=None):
    game = {
        'board': [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        'move': None,
        'newTile': (4, 4),
        'animationTimer': 0,
        'score': 0,
        'agentActive': False,
        'totalMoves': 0,
        'lost': False
    }

    genTile(game)
    genTile(game)

    if session is not None:
        session['game'] = game
        if session['recording']:
            session['game']['animationTimer'] = 10
            createMoveLog(session['gamesCompleted'], session['path'])
            recordMove(session, initialMove=True)

    return game


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
