# Lucas Goddin
# June 12, 2020
# Operations used by 2048 game and agents

import copy
import random


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
