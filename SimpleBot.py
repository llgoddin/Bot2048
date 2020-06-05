# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

# TODO LIST
# fix max range combination bug
# add game initializer and restart
# add tile animation

# GOOD TEST CASE (used to cause bugs)
# 0,2,0,0
# 0,2,0,0
# 0,4,0,0
# 16,16,16,8


import sys
import random
import copy
import pygame

LIGHT_GREY = (200, 200, 200)
GREY = (120, 120, 120)
DARK_GREY = (40, 40, 40)
BLACK = (0, 0, 0)

colorDict = {
    2: (238, 228, 218),
    4: (210, 180, 170),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    # 0: (255, 0, 0)
    0: GREY
}

# creates a window and sets size and title
pygame.init()
pygame.display.set_caption('2048')
screen = pygame.display.set_mode((500, 600))
screen.fill(LIGHT_GREY)
pygame.display.flip()


def gameLoop(board):
    # used to control the main game loop
    userPlaying = True

    screenUpdate(board)
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
                screenUpdate(board)
            elif event.type == pygame.KEYUP:
                print('KEY RELEASE')

        # writeBoard(board)

        # board = readBoard()

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


def screenUpdate(board):
    # draws grid outline
    pygame.draw.rect(screen, DARK_GREY, (17, 120, 465, 465), 0)

    # draws title font
    titleText = textRend('2048', 120, DARK_GREY, )
    textRect = titleText.get_rect()
    textRect.center = (148, 77)
    screen.blit(titleText, textRect)

    # draws tiles
    for i in range(0, 4):
        for j in range(0, 4):
            # draw the tile
            pygame.draw.rect(screen, colorDict[board[i][j]], (27 + (j * 115), 130 + (i * 115), 100, 100), 0)

            # create tile text
            tileText = textRend("" if board[i][j] == 0 else str(board[i][j]), 40, BLACK)
            tileTextRect = tileText.get_rect()
            tileTextRect.center = (75 + (j * 115), 180 + (i * 115))
            screen.blit(tileText, tileTextRect)

    # update the screen
    pygame.display.flip()


def printBoard(board):
    # prints board values to console
    print('-' * 11)
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end=', ')
        print()


def textRend(message, size, color):
    font1 = pygame.font.Font('/System/Library/Fonts/AppleSDGothicNeo.ttc', size)
    textObj = font1.render(message, True, color)
    return textObj


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
    print('\nPRE COMPRESSION VV')
    printBoard(board)

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

    print('\nPOST COMPRESSION VV')
    printBoard(board)

    if boardCopy != board:
        genTile(board)


def genTile(board):
    r = random.random()
    if r > .9:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)
            print('[' + str(i) + ', ' + str(j) + ']')
            if board[i][j] == 0:
                board[i][j] = 4
                success = True
    else:
        success = False
        while not success:
            i = random.randint(0, 3)
            j = random.randint(0, 3)
            print('[' + str(i) + ', ' + str(j) + ']')
            if board[i][j] == 0:
                board[i][j] = 2
                success = True


b = readBoard()

gameLoop(b)
