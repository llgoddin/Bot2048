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
import pygame
import math
import time
from Operations import *
from Agent import myAlgorithm

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

board = readBoard()
AgentActive = False
mouseDown = False
recordingGame = True
gamesInSession = 100
gamesCompleted = 0
recordingPath = None


def gameLoop():
    global AgentActive, recordingGame, gamesInSession, gamesCompleted

    # used to control the main game loop
    running = True
    waitingToReset = True

    FPS = 60
    animTimer = 0
    fpsClock = pygame.time.Clock()

    score = 0
    totalMoves = 0
    newTilePos = (4, 4)

    screenUpdate(newTilePos, animTimer)
    while running:
        moveTaken = None

        # handle keyboard events while no agent is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and newTilePos == (4, 4):
                if event.key == pygame.K_UP:
                    if not AgentActive:
                        newTilePos = move(board, 'u')
                if event.key == pygame.K_DOWN:
                    if not AgentActive:
                        newTilePos = move(board, 'd')
                if event.key == pygame.K_LEFT:
                    if not AgentActive:
                        newTilePos = move(board, 'l')
                if event.key == pygame.K_RIGHT:
                    if not AgentActive:
                        newTilePos = move(board, 'r')

        # agent move
        if AgentActive and animTimer == 0:
            moveTaken = myAlgorithm(board)
            newTilePos = move(board, moveTaken)
            if recordingGame:
                recordMove(board, moveTaken, gamesCompleted, recordingPath)
                totalMoves += 1

        if not recordingGame:
            # track and update animation
            if newTilePos != (4, 4) and animTimer == 0:
                animTimer = 1

            if 0 < animTimer < 10:
                animTimer += math.floor((11 - animTimer) / 2)
            elif animTimer >= 10:
                animTimer = 0
                newTilePos = (4, 4)

            screenUpdate(newTilePos, animTimer)

        score = calculateScore()

        checkClick()

        running = gameNotEnded()

        fpsClock.tick(FPS)

    if recordingGame:
        recordGameSummary(board, totalMoves, score, recordingPath)
        gamesCompleted += 1

        pygame.display.set_caption(str(gamesCompleted) + ' / ' + str(gamesInSession))

        if gamesCompleted < gamesInSession:
            createMoveLog(gamesCompleted, recordingPath)
            newGame()
            gameLoop()

        if gamesCompleted == gamesInSession:
            recordingGame = False
            AgentActive = False
            gamesCompleted = 0
            compileStats(recordingPath)
            pygame.display.set_caption('2048')

    while waitingToReset:

        for event in pygame.event.get():
            checkClick()

        screenUpdate((4, 4), 0)


def calculateScore():
    s = 0
    for i in range(4):
        for j in range(4):
            s += board[i][j]

    return s


def screenUpdate(pos, timer):
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
        agentBtnColor = DARK_GREY
    elif 352 < mouse[0] < 412 and 55 < mouse[1] < 115:
        agentBtnColor = GREY
        restartBtnColor = DARK_GREY
    else:
        restartBtnColor = DARK_GREY
        agentBtnColor = DARK_GREY

    # draw restart button
    pygame.draw.rect(screen, restartBtnColor, (422, 55, 60, 60))
    pygame.draw.circle(screen, WHITE, (452, 85), 18)
    pygame.draw.circle(screen, restartBtnColor, (452, 85), 15)
    pygame.draw.polygon(screen, restartBtnColor, [(452, 85), (422, 85), (445, 110)])
    pygame.draw.polygon(screen, WHITE, [(430, 85), (440, 85), (435, 95)])

    # draw agent button
    pygame.draw.rect(screen, agentBtnColor, (352, 55, 60, 60))
    pygame.draw.polygon(screen, WHITE, [(362, 65), (402, 85), (362, 105)])

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

    pygame.display.flip()


def textRend(message, size, color):
    font1 = pygame.font.Font('/System/Library/Fonts/AppleSDGothicNeo.ttc', size)
    textObj = font1.render(message, True, color)
    return textObj


def checkClick():
    global AgentActive, mouseDown

    # handle mouse events
    click = pygame.mouse.get_pressed()

    # testing click for 0's makes user let go in between button clicks
    if click == (0, 0, 0):
        mouseDown = False
    elif click == (1, 0, 0) and not mouseDown:
        mouseDown = True
        mouse = pygame.mouse.get_pos()

        # test click to see if it hit any buttons
        if 422 < mouse[0] < 482 and 55 < mouse[1] < 115:
            newGame()
            if not recordingGame:
                AgentActive = False
            gameLoop()
        elif 352 < mouse[0] < 412 and 55 < mouse[1] < 115:
            AgentActive = not AgentActive


def newGame():
    global board
    board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    genTile(board)
    genTile(board)

    writeBoard(board)
    return board


def gameNotEnded():
    moves = ['l', 'r', 'u', 'd']
    movesLeft = 4

    for m in moves:
        tempBoard = copy.deepcopy(board)

        move(tempBoard, m, False)

        if tempBoard == board:
            movesLeft -= 1

    return movesLeft > 0


if recordingGame:
    recordingPath = createSession()

gameLoop()

pygame.quit()
sys.exit()
