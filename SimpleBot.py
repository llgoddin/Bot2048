# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

# TODO LIST
# Finish Game Loop
# Work on Setting up the game independently

# BUGGED TEST CASE
# the bug seems happen during tile compression see line 122
# 0,2,0,0
# 0,2,0,0
# 0,4,0,0
# 16,16,16,8


import sys
import pygame

colorDict = {
    2: (240, 220, 200),
    4: (255, 234, 199),
    8: (252, 186, 100),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    0: (255, 0, 0)
    # 0: (238, 228, 218)
}

# creates a window and sets size and title
pygame.init()
pygame.display.set_caption('2048')
screen = pygame.display.set_mode((600, 800))
screen.fill((40, 40, 40))
pygame.display.flip()


def gameLoop(board):
    # used to control the main game loop
    userPlaying = True

    printBoard(board)
    while userPlaying:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                userPlaying = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    simMove(board, 'u')
                if event.key == pygame.K_DOWN:
                    simMove(board, 'd')
                if event.key == pygame.K_LEFT:
                    simMove(board, 'l')
                if event.key == pygame.K_RIGHT:
                    simMove(board, 'r')
                printBoard(board)

        writeBoard(board)

        board = readBoard()

    sys.exit()


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


def printBoard(board):
    # prints board values to console
    print('-' * 11)
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end=', ')
        print()

    # drawing the board to screen
    for i in range(0, 4):
        for j in range(0, 4):
            pygame.draw.rect(screen, colorDict[board[i][j]], (50 + (j * 133), 50 + (i * 133), 100, 100), 0)

    pygame.display.flip()
    print('SCREEN UPDATE')


def combineTiles(board, xDirec, yDirec):
    iterator = 0
    start = 0
    end = 0
    vert = True

    if not xDirec == 0:
        vert = False

    if xDirec < 0 or yDirec < 0:
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
            for distance in range(1, 3):
                if vert:
                    if (i + (iterator * distance)) < 0 or (i + (iterator * distance)) > 3:
                        break
                    elif board[i + (iterator * distance)][j] == board[i][j]:
                        board[i][j] *= 2
                        board[i + (iterator * distance)][j] = 0
                    elif board[i + (iterator * distance)][j] != 0:
                        break
                else:
                    if (j + (iterator * distance)) < 0 or (j + (iterator * distance)) > 3:
                        break
                    elif board[i][j + (iterator * distance)] == board[i][j]:
                        board[i][j] *= 2
                        board[i][j + (iterator * distance)] = 0
                    elif board[i][j + (iterator * distance)] != 0:
                        break


def simMove(board, direction):
    xDirec = 0
    yDirec = 0

    start = 0
    end = 0
    iterator = 0

    # determines which direction tiles should be moving and direction the loop should iterate
    if direction == 'l':
        xDirec = -1
        iterator = -1
    elif direction == 'r':
        xDirec = 1
        iterator = 1
    elif direction == 'u':
        yDirec = -1
        iterator = -1
    else:
        yDirec = 1
        iterator = 1

    if iterator > 0:
        start = 0
        end = 3
    else:
        start = 3
        end = 0

    # combine tiles
    combineTiles(board, xDirec, yDirec)

    # compress tiles
    for cycles in range(2):
        for i in range(start, end + xDirec, iterator):
            for j in range(start, end + yDirec, iterator):
                if board[i + yDirec][j + xDirec] == 0:
                    board[i + yDirec][j + xDirec] = board[i][j]
                    board[i][j] = 0


b = readBoard()

gameLoop(b)
