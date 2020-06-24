# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

# GOOD TEST CASE (used to cause bugs)
# 0,2,0,0
# 0,2,0,0
# 0,4,0,0
# 16,16,16,8


import math
import sys

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

# creates a window and sets size and title
pygame.init()
pygame.display.set_caption('2048')
screen = pygame.display.set_mode((500, 600))
screen.fill(LIGHT_GREY)
pygame.draw.rect(screen, DARK_GREY, (17, 120, 465, 465))
pygame.display.flip()

mouseDown = False


def gameLoop(session):

    if session['recording']:
        session['game']['agentActive'] = True

    waitingToReset = True

    FPS = 30
    fpsClock = pygame.time.Clock()

    screenUpdate(session)
    while not session['game']['lost']:
        session['game']['move'] = None

        # handle keyboard events while no agent is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not session['game']['agentActive'] or session['game']['newTile'] == (4, 4):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        session['game']['move'] = 'u'
                    if event.key == pygame.K_DOWN:
                        session['game']['move'] = 'd'
                    if event.key == pygame.K_LEFT:
                        session['game']['move'] = 'l'
                    if event.key == pygame.K_RIGHT:
                        session['game']['move'] = 'r'

        # agent move
        if session['game']['agentActive']:
            session['game']['move'] = myAlgorithm(session['game'])

        move(session['game'])

        recordMove(session)

        calculateScore(session['game'])

        checkGameLost(session['game'])

        checkClick(session)

        updateAnimation(session)

        screenUpdate(session)

        fpsClock.tick(FPS)

    recordGameSummary(session)

    if session['recording']:
        gameLoop(session)

    while waitingToReset:

        for event in pygame.event.get():
            checkClick(session)
            if event.type == pygame.QUIT:
                sys.exit()

        screenUpdate(session)


def updateAnimation(session):
    if session['recording']:
        session['game']['animationTimer'] = 10
    else:
        # track and update animation
        if session['game']['newTile'] != (4, 4) and session['game']['animationTimer'] == 0:
            session['game']['animationTimer'] = 1

        if 0 < session['game']['animationTimer'] < 10:
            session['game']['animationTimer'] += math.floor((11 - session['game']['animationTimer']) / 2)
        elif session['game']['animationTimer'] >= 10:
            session['game']['animationTimer'] = 0
            session['game']['newTile'] = (4, 4)


def calculateScore(game):
    s = 0
    for i in range(4):
        for j in range(4):
            s += game['board'][i][j]

    game['score'] = s


def screenUpdate(session):

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

    # I use the window caption as a progress bar to show the session progress when recording and not updating the screen
    if session['recording'] and not session['game']['lost']:
        pygame.display.set_caption(str(session['gamesCompleted']) + ' / ' + str(session['totalGames']))
        pygame.display.flip()
        return None
    else:
        pygame.display.set_caption('2048')

        # draws grid outline
        pygame.draw.rect(screen, DARK_GREY, (17, 120, 465, 465))

        # draws tiles
        for i in range(0, 4):
            for j in range(0, 4):
                if session['game']['newTile'] == (i, j):
                    # animate new tiles
                    tileCord = (27 + (j * 115), 130 + (i * 115))
                    scale = session['game']['animationTimer'] * .1

                    sideLen = int(100 * scale)

                    x = tileCord[0] + (100 - sideLen) / 2
                    y = tileCord[1] + (100 - sideLen) / 2

                    pygame.draw.rect(screen, colorDict[0], [tileCord[0], tileCord[1], 100, 100])
                    pygame.draw.rect(screen, colorDict[session['game']['board'][i][j]], [x, y, sideLen, sideLen])

                    if session['game']['animationTimer'] == 10:
                        # create tile text
                        tileText = textRend("" if session['game']['board'][i][j] == 0 else str(session['game']['board'][i][j]), 40, BLACK)
                        tileTextRect = tileText.get_rect()
                        tileTextRect.center = (75 + (j * 115), 180 + (i * 115))
                        screen.blit(tileText, tileTextRect)
                else:
                    # draw old tiles
                    pygame.draw.rect(screen, colorDict[session['game']['board'][i][j]], (27 + (j * 115), 130 + (i * 115), 100, 100))

                    # create tile text
                    tileText = textRend("" if session['game']['board'][i][j] == 0 else str(session['game']['board'][i][j]), 40, BLACK)
                    tileTextRect = tileText.get_rect()
                    tileTextRect.center = (75 + (j * 115), 180 + (i * 115))
                    screen.blit(tileText, tileTextRect)

    pygame.display.flip()


def textRend(message, size, color):
    font1 = pygame.font.Font('/System/Library/Fonts/AppleSDGothicNeo.ttc', size)
    textObj = font1.render(message, True, color)
    return textObj


def checkClick(session):
    global mouseDown

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
                session['game']['agentActive'] = False
                game = createGame()
                gameLoop(game, session)
        elif 352 < mouse[0] < 412 and 55 < mouse[1] < 115:
            if not session['recording']:
                session['game']['agentActive'] = not session['game']['agentActive']


def checkGameLost(game):
    moves = ['l', 'r', 'u', 'd']
    movesLeft = 4

    for m in moves:
        tempGame = copy.deepcopy(game)

        tempGame['move'] = m

        move(tempGame, False)

        if tempGame['board'] == game['board']:
            movesLeft -= 1

    if movesLeft > 0:
        game['lost'] = False
    else:
        game['lost'] = True


s = createSession(recording=True, totalGames=2)

gameLoop(s)

pygame.quit()
sys.exit()
