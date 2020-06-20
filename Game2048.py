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


import math
import sys
import time

import pygame

from Agent import myAlgorithm
from Operations import *

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

session = {
    'recording': False,
    'path': None,
    'totalGames': 1,
    'gamesCompleted': 0,
    'currentGame': None,
    'startTime': None,
    'endTime': None
}

game = {
    'board': None,
    'newTile': (4, 4),
    'animationTimer': 0,
    'score': 0,
    'totalMoves': 0,
    'lost': False,

}

# creates a window and sets size and title
pygame.init()
pygame.display.set_caption('2048')
screen = pygame.display.set_mode((500, 600))
screen.fill(LIGHT_GREY)
pygame.display.flip()

game['board'] = readBoard()
AgentActive = False
mouseDown = False

# TODO
# create session and game data structures


def gameLoop():
    global AgentActive

    # used to control the main game loop
    running = True
    waitingToReset = True

    FPS = 60
    fpsClock = pygame.time.Clock()

    screenUpdate(game['newTile'], game['animationTimer'])
    while running:
        moveTaken = None

        # handle keyboard events while no agent is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game['newTile'] == (4, 4):
                if event.key == pygame.K_UP:
                    if not AgentActive:
                        game['newTile'] = move(game, 'u')
                if event.key == pygame.K_DOWN:
                    if not AgentActive:
                        game['newTile'] = move(game, 'd')
                if event.key == pygame.K_LEFT:
                    if not AgentActive:
                        game['newTile'] = move(game, 'l')
                if event.key == pygame.K_RIGHT:
                    if not AgentActive:
                        game['newTile'] = move(game, 'r')

        # agent move
        if AgentActive and game['animationTimer'] == 0:
            moveTaken = myAlgorithm(game['board'])
            game['newTile'] = move(game, moveTaken)
            if session['recording']:
                pygame.display.set_caption(str(session['gamesCompleted']) + ' / ' + str(session['totalGames']))
                recordMove(game['board'], moveTaken, session['gamesCompleted'], session['path'])
                game['totalMoves'] += 1

        if not session['recording']:
            # track and update animation
            if game['newTile'] != (4, 4) and game['animationTimer'] == 0:
                game['animationTimer'] = 1

            if 0 < game['animationTimer'] < 10:
                game['animationTimer'] += math.floor((11 - game['animationTimer']) / 2)
            elif game['animationTimer'] >= 10:
                game['animationTimer'] = 0
                game['newTile'] = (4, 4)

        if not session['recording'] or not AgentActive:
            screenUpdate(game['newTile'], game['animationTimer'])

        game['score'] = calculateScore()

        checkClick()

        running = gameNotEnded()

        fpsClock.tick(FPS)

    if session['recording']:
        recordGameSummary(game['board'], game['totalMoves'], game['score'], session['path'])
        session['gamesCompleted'] += 1

        if session['gamesCompleted'] < session['totalGames']:
            createMoveLog(session['gamesCompleted'], session['path'])
            newGame()
            gameLoop()

        if session['gamesCompleted'] == session['totalGames']:
            # reset agent and game recording info
            session['recording'] = False
            AgentActive = False
            session['gamesCompleted'] = 0

            # gather time information and compile stats
            session['endTime'] = time.time()
            t = computeTotalTime(session['startTime'], session['endTime'])
            compileStats(t, session['path'])

            # reset the display caption
            pygame.display.set_caption('2048')

    while waitingToReset:

        for event in pygame.event.get():
            checkClick()
            if event.type == pygame.QUIT:
                waitingToReset = False

        screenUpdate((4, 4), 0)


def calculateScore():
    s = 0
    for i in range(4):
        for j in range(4):
            s += game['board'][i][j]

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
                pygame.draw.rect(screen, colorDict[game['board'][i][j]], [x, y, sideLen, sideLen])
            else:
                # draw old tiles
                pygame.draw.rect(screen, colorDict[game['board'][i][j]], (27 + (j * 115), 130 + (i * 115), 100, 100))

                # create tile text
                tileText = textRend("" if game['board'][i][j] == 0 else str(game['board'][i][j]), 40, BLACK)
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
            if not session['recording']:
                AgentActive = False
                newGame()
                gameLoop()
        elif 352 < mouse[0] < 412 and 55 < mouse[1] < 115:
            if not session['recording']:
                AgentActive = not AgentActive


def newGame():
    game['board'] = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    genTile(game['board'])
    genTile(game['board'])

    writeBoard(game['board'])


def gameNotEnded():
    moves = ['l', 'r', 'u', 'd']
    movesLeft = 4

    for m in moves:
        tempGame = copy.deepcopy(game)

        move(tempGame, m, False)

        if tempGame['board'] == game['board']:
            movesLeft -= 1

    return movesLeft > 0


# tempBoard = board.copy()
# print('Move Chosen: ' + myAlgorithm(tempBoard))
# move(board, myAlgorithm(tempBoard), False)
# print('Next Move = ' + myAlgorithm(tempBoard))

if session['recording']:
    session['path'] = createSession()
    session['startTime'] = time.time()

gameLoop()

pygame.quit()
sys.exit()
