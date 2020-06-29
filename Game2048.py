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
from GameOperations import *

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


def gameLoop(game):

    waitingToReset = True

    FPS = 30
    fpsClock = pygame.time.Clock()

    screenUpdate(game)
    while not game['lost']:
        game['move'] = None

        # handle keyboard events while no agent is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game['agentActive'] or game['newTile'] == (4, 4):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game['move'] = 'u'
                    if event.key == pygame.K_DOWN:
                        game['move'] = 'd'
                    if event.key == pygame.K_LEFT:
                        game['move'] = 'l'
                    if event.key == pygame.K_RIGHT:
                        game['move'] = 'r'

        # agent move
        if game['agentActive']:
            game['move'] = myAlgorithm(game)

        move(game)

        calculateScore(game)

        checkGameLost(game)

        checkClick(game)

        updateAnimation(game)

        screenUpdate(game)

        fpsClock.tick(FPS)

    while waitingToReset:
        for event in pygame.event.get():
            checkClick(game)
            if event.type == pygame.QUIT:
                sys.exit()

        screenUpdate(game)


def updateAnimation(game):
    # track and update animation
    if game['newTile'] != (4, 4) and game['animationTimer'] == 0:
        game['animationTimer'] = 1

    if 0 < game['animationTimer'] < 10:
        game['animationTimer'] += math.floor((11 - game['animationTimer']) / 2)
    elif game['animationTimer'] >= 10:
        game['animationTimer'] = 0
        game['newTile'] = (4, 4)


def screenUpdate(game):

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
    pygame.display.set_caption('2048')

    # draws grid outline
    pygame.draw.rect(screen, DARK_GREY, (17, 120, 465, 465))

    # draws tiles
    for i in range(0, 4):
        for j in range(0, 4):
            if game['newTile'] == (i, j) and not game['animationTimer'] == 10:
                # animate new tiles
                tileCord = (27 + (j * 115), 130 + (i * 115))
                scale = game['animationTimer'] * .1

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


def checkClick(game):
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
            game = createGame()
            gameLoop(game)
        elif 352 < mouse[0] < 412 and 55 < mouse[1] < 115:
            game['agentActive'] = not game['agentActive']


def createButton(rect=[10, 10, 90, 90], text='BTN', fgColor=LIGHT_GREY, bgColor=DARK_GREY, symbol=[['c', [20, 20, 20]], ['p', [10, 10, 10, 20, 20, 30]]]):
    btn = {
        'rect': pygame.rect(rect),
        'text': text,
        'fgColor': fgColor,
        'bgColor': bgColor,
        'symbol': symbol,
        'textSize': None
    }


def renderButtons(btns=[]):
    for b in btns:
        pygame.draw.rect(screen, b['bgColor'], b['rect'])

        textObj = None
        if b['text'] is not None:
            textSmallEnough = False
            if b['textSize'] is None:
                textSize = 100
            else:
                textSize = b['textSize']

            while not textSmallEnough:
                textObj = textRend(b['text'], b['textSize'], b['fgColor'])
                textRect = textObj.get_rect()
                if textRect[2] >= b['rect'][2] or textRect[3] >= b['rect'][3]:
                    textSize -= 1
                    del textObj
                    del textRect
                else:
                    b['textSize'] = textSize

        for shape in b['symbol']:
            x = b['rect'].topleft[0] + shape[1][0]
            y = b['rect'].topleft[1] + shape[1][1]
            symbolColor = b['fgColor']
            
            if shape[0] == 'c':
                pygame.draw.circle(screen, symbolColor, (x, y), shape[1][3])
            elif shape[0] == 'r':
                pygame.draw.rect(screen, b['fgColor'], shape[1])
            elif shape[0] == 'p':
                pointList = [(x, y)]
                for i in range(2, len(shape[1]), step=2):
                    newX = x + shape[1][i]
                    newY = y + shape[1][i + 1]
                    pointList.append((newX, newY))
                
                pygame.draw.polygon(screen, symbolColor, pointList)

        if textObj is not None:
            textRect.center = b['rect'].center
            screen.blit(textObj, textRect)


s = createSession(recording=True, totalGames=100)

gameLoop(s)

pygame.quit()
sys.exit()
