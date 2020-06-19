# Lucas Goddin
# June 12, 2020
# Operations used by 2048 game and agents

import copy
import random
import os


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
                if int(d[-1]) >= nextSession:
                    nextSession = int(d[-1]) + 1

            except ValueError as verr:
                print('Directory ' + str(d) + ' does not end in a number!')

        return nextSession


def createMoveLog(num, path):
    moveLog = open(path + '/MoveLogs/moveLogGame' + str(num) + '.txt', 'w+')
    moveLog.write('START MOVE LOG\n')
    moveLog.write('-' * 10 + '\n')
    moveLog.close()


def createSession():
    sessionNum = findSessionNum()

    path = '/Users/lucasgoddin/Documents/PycharmProjects/GameRecording/Session' + str(sessionNum)
    os.mkdir(path)
    os.mkdir((path + str('/MoveLogs')))

    createMoveLog(0, path)

    stats = open(path + '/sessionStats.txt', 'w+')
    stats.write('STATS\n')
    stats.write('-' * 10 + '\n')
    stats.close()

    gameSummaries = open(path + '/gameSummaries.txt', 'w+')
    gameSummaries.write('GAME SUMMARIES\n')
    gameSummaries.write('Game #- Max Tile, Score, Number Of Moves\n')
    gameSummaries.write('-' * 10 + '\n')
    gameSummaries.close()

    return path


def recordMove(board, m, gameNumber, path):
    moveLog = open((str(path) + '/MoveLogs/moveLogGame' + str(gameNumber) + '.txt'), 'a+')

    moveLog.write('\n')
    for i in range(4):
        for j in range(4):
            if j < 3:
                moveLog.write(str(board[i][j]) + ', ')
            else:
                moveLog.write(str(board[i][j]))

        moveLog.write('\n')

    moveLog.write('LAST MOVE: ' + str(m) + '\n')
    moveLog.write('-' * 10 + '\n')


def recordGameSummary(endingBoard, moveNum, score, path):
    gameSumFile = open((str(path) + '/gameSummaries.txt'), 'r')

    lines = gameSumFile.readlines()

    nextGameNum = 0
    for l in lines[3:]:
        try:
            if int(l[5]) >= nextGameNum:
                nextGameNum = int(l[5]) + 1
        except ValueError as verr:
            print('Error Parsing Game Summary File')
            print(verr)

    gameSumFile.close()

    maxTile = 0
    for i in range(4):
        for j in range(4):
            if endingBoard[i][j] > maxTile:
                maxTile = endingBoard[i][j]

    gameSumFile = open((str(path) + '/gameSummaries.txt'), 'a+')

    gameSumFile.write('Game ' + str(nextGameNum) + '- ' + str(maxTile) + ', ' + str(score) + ', ' + str(moveNum) + '\n')

    gameSumFile.close()


def compileStats(path):
    sessionNum = findSessionNum() - 1
    gameSummaries = open((path + '/gameSummaries.txt'), 'r')

    lines = gameSummaries.readlines()

    gameSummaries.close()

    statFile = open(path + '/sessionStats.txt', 'a+')

    maxTile = 0

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

    print('Number Of Games: ' + str(numOfGames))

    for l in lines[3:]:
        statString = (l.split('-')[1])
        stats = statString.split(', ')

        for s in stats:
            s = s.strip()

        print(statString[0])
        print('Max Tile: ' + stats[0])
        print('Score: ' + stats[1])
        print('Moves: ' + stats[2])

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

    percent128 = num128/numOfGames
    percent256 = num256/numOfGames
    percent512 = num512/numOfGames
    percent1024 = num1024/numOfGames
    percent2048 = num2048/numOfGames
    percent4096 = num4096/numOfGames

    averageScore = totalScore/numOfGames
    averageMaxTile = totalMaxTile/numOfGames
    averageMoves = totalMoveNumber/numOfGames

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


def genTile(board):
    newPos = (4, 4)
    r = random.random()
    if r > .9:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)

            if board[i][j] == 0:
                board[i][j] = 4
                success = True
                newPos = (i, j)
    else:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)

            if board[i][j] == 0:
                board[i][j] = 2
                success = True
                newPos = (i, j)
    return newPos


def move(board, direction, newTile=True):
    boardCopy = copy.deepcopy(board)

    xDirec = 0
    yDirec = 0

    start = 0
    end = 0
    iterator = 0

    # determines which direction tiles should be moving and direction the loop should iterate
    if direction == 'l':
        xDirec = 1
        iterator = 1
    elif direction == 'r':
        xDirec = -1
        iterator = -1
    elif direction == 'u':
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
    combineTiles(board, xDirec, yDirec)

    # compress tiles

    # The problem with this compression code is simple, its ugly. time to try again
    # The addition of cycles works but is extremely sloppy, im going to try to clean it up after debugging carefully
    # I originally thought combination and compression would have to scan the array in opposite directions
    # The commented code below works for opposite directions but the new code will work for the same direction (FIXED)

    for cycles in range(3):
        for i in range(start, end + xDirec, iterator):
            for j in range(start, end + yDirec, iterator):
                if board[i][j] == 0:
                    board[i][j] = board[i + yDirec][j + xDirec]
                    board[i + yDirec][j + xDirec] = 0

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
    if boardCopy != board and newTile:
        newPos = genTile(board)
    return newPos
