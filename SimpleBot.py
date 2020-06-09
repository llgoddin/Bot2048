# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

# TODO LIST
# fix max range combination bug (FIXED)
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
import math

WHITE = (255, 255, 255)
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
    mouseDown = False

    FPS = 30
    animTimer = 0
    fpsClock = pygame.time.Clock()

    newTilePos = (4, 4)

    screenUpdate(board, newTilePos, animTimer)
    while userPlaying:
        # handle keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                userPlaying = False
            if event.type == pygame.KEYDOWN and newTilePos == (4, 4):
                if event.key == pygame.K_UP:
                    newTilePos = simMove(board, 'u')
                if event.key == pygame.K_DOWN:
                    newTilePos = simMove(board, 'd')
                if event.key == pygame.K_LEFT:
                    newTilePos = simMove(board, 'l')
                if event.key == pygame.K_RIGHT:
                    newTilePos = simMove(board, 'r')
                if newTilePos != (4, 4):
                    animTimer = 1
            elif event.type == pygame.KEYUP:
                print('KEY RELEASE')

        # handle mouse events
        click = pygame.mouse.get_pressed()
        if click == (0, 0, 0):
            mouseDown = False
        elif click == (1, 0, 0) and not mouseDown:
            mouseDown = True
            mouse = pygame.mouse.get_pos()
            if 422 < mouse[0] < 482 and 55 < mouse[1] < 115:
                board = newGame()

        screenUpdate(board, newTilePos, animTimer)

        if 0 < animTimer < 10:
            animTimer += math.floor((11 - animTimer) / 2)
        elif animTimer >= 10:
            animTimer = 0
            newTilePos = (4, 4)

        # writeBoard(board)

        # board = readBoard()
        fpsClock.tick(FPS)

    writeBoard(board)
    pygame.exit()
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

    boardFile.close()


def screenUpdate(board, pos, timer):
    # draws grid outline
    pygame.draw.rect(screen, DARK_GREY, (17, 120, 465, 465))

    # draws title font
    titleText = textRend('2048', 120, DARK_GREY)
    textRect = titleText.get_rect()
    textRect.center = (148, 77)
    screen.blit(titleText, textRect)

    mouse = pygame.mouse.get_pos()
    if 422 < mouse[0] < 482 and 55 < mouse[1] < 115:
        restartBtnColor = GREY
    else:
        restartBtnColor = DARK_GREY

    # draw buttons
    pygame.draw.rect(screen, restartBtnColor, (422, 55, 60, 60))
    pygame.draw.circle(screen, WHITE, (452, 85), 18)
    pygame.draw.circle(screen, restartBtnColor, (452, 85), 15)
    pygame.draw.polygon(screen, restartBtnColor, [(452, 85), (422, 85), (445, 110)])
    pygame.draw.polygon(screen, WHITE, [(430, 85), (440, 85), (435, 95)])

    # draws tiles
    for i in range(0, 4):
        for j in range(0, 4):
            if pos == (i, j):
                # animate new tiles
                tileCord = (27 + (j * 115), 130 + (i * 115))
                scale = timer * .1

                sideLen = int(100 * scale)

                x = tileCord[0] + (100 - sideLen) / 2
                y = tileCord[1] + (100 - sideLen) / 2

                pygame.draw.rect(screen, colorDict[0], [tileCord[0], tileCord[1], 100, 100])
                pygame.draw.rect(screen, colorDict[board[i][j]], [x, y, sideLen, sideLen])
            else:
                # draw old tiles
                pygame.draw.rect(screen, colorDict[board[i][j]], (27 + (j * 115), 130 + (i * 115), 100, 100))

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

    newPos = (4, 4)
    if boardCopy != board:
        newPos = genTile(board)
    return newPos


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


def newGame():
    board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    genTile(board)
    genTile(board)

    writeBoard(board)
    return board


b = readBoard()

gameLoop(b)

pygame.quit()
sys.exit()
