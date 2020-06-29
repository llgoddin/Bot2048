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

RED = (255, 0, 0)
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

buttons = {}


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
    global buttons

    screen.fill(LIGHT_GREY)

    # draws title font
    titleText = textRend('2048', 120, DARK_GREY)
    textRect = titleText.get_rect()
    textRect.center = (148, 77)
    screen.blit(titleText, textRect)

    mouse = pygame.mouse.get_pos()

    if buttons['newGame']['rect'][0] < mouse[0] < buttons['newGame']['rect'][0] + buttons['newGame']['rect'][2]:
        if buttons['newGame']['rect'][1] < mouse[1] < buttons['newGame']['rect'][1] + buttons['newGame']['rect'][3]:
            changeButtonColor(buttons['newGame'], WHITE, GREY)
            changeButtonColor(buttons['agent'], WHITE, DARK_GREY)
    elif buttons['agent']['rect'][0] < mouse[0] < buttons['agent']['rect'][0] + buttons['agent']['rect'][2]:
        if buttons['agent']['rect'][1] < mouse[1] < buttons['agent']['rect'][1] + buttons['agent']['rect'][3]:
            changeButtonColor(buttons['agent'], WHITE, GREY)
            changeButtonColor(buttons['newGame'], WHITE, DARK_GREY)
    else:
        changeButtonColor(buttons['agent'], WHITE, DARK_GREY)
        changeButtonColor(buttons['newGame'], WHITE, DARK_GREY)

    renderButtons(buttons)

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

    renderButtons(buttons)

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
        return None
    elif click == (1, 0, 0) and not mouseDown:
        mouseDown = True
        mouse = pygame.mouse.get_pos()

        # test click to see if it hit any buttons
        if buttons['newGame']['rect'][0] < mouse[0] < buttons['newGame']['rect'][0] + buttons['newGame']['rect'][2]:
            if buttons['newGame']['rect'][1] < mouse[1] < buttons['newGame']['rect'][1] + buttons['newGame']['rect'][3]:
                game = createGame()
                gameLoop(game)
        if buttons['agent']['rect'][0] < mouse[0] < buttons['agent']['rect'][0] + buttons['agent']['rect'][2]:
            if buttons['agent']['rect'][1] < mouse[1] < buttons['agent']['rect'][1] + buttons['agent']['rect'][3]:
                game['agentActive'] = not game['agentActive']


def createButton(rect=[10, 10, 90, 90], text='BTN', fgColor=LIGHT_GREY, bgColor=DARK_GREY, symbol=[['c', [20, 20, 20]], ['p', [10, 10, 10, 20, 20, 30]]]):
    btn = {
        'rect': pygame.Rect(rect),
        'text': text,
        'fgColor': fgColor,
        'bgColor': bgColor,
        'symbols': symbol,
        'textSize': None
    }

    return btn


def renderButtons(btns={}):
    for k, b in btns.items():
        pygame.draw.rect(screen, b['bgColor'], b['rect'])

        textObj = None
        if b['text'] is not None:
            textSmallEnough = False
            if b['textSize'] is None:
                textSize = 100
            else:
                textSize = b['textSize']

            textPadding = 10
            while not textSmallEnough:
                textObj = textRend(b['text'], textSize, b['fgColor'])
                textRect = textObj.get_rect()
                if (textRect[2] - textPadding) >= b['rect'][2] or (textRect[3] - textPadding) >= b['rect'][3]:
                    textSize -= 1
                    del textObj
                    del textRect
                else:
                    b['textSize'] = textSize
                    textSmallEnough = True

        for shape in b['symbols']:
            x = b['rect'].topleft[0]
            y = b['rect'].topleft[1]

            symbolColor = RED
            if shape[1] == 'fg':
                symbolColor = b['fgColor']
            elif shape[1] == 'bg':
                symbolColor = b['bgColor']
            
            if shape[0] == 'c':
                pygame.draw.circle(screen, symbolColor, (x + shape[2][0], y + shape[2][1]), shape[2][2])
            elif shape[0] == 'r':
                pygame.draw.rect(screen, symbolColor, shape[2])
            elif shape[0] == 'p':
                pointList = []

                start = 0
                stop = len(shape[2])

                for i in range(start, stop, 2):
                    newX = x + shape[2][i]
                    newY = y + shape[2][i + 1]
                    pointList.append((newX, newY))

                pygame.draw.polygon(screen, symbolColor, pointList)

        if textObj is not None:
            textRect.center = b['rect'].center
            screen.blit(textObj, textRect)


def changeButtonColor(btn, newFG=WHITE, newBG=DARK_GREY):
    btn['fgColor'] = newFG
    btn['bgColor'] = newBG


buttons['agent'] = createButton([352, 55, 60, 60], None, WHITE, DARK_GREY, [['p', 'fg', [10, 10, 50, 30, 10, 50]]])
buttons['newGame'] = createButton([422, 55, 60, 60], None, WHITE, DARK_GREY, [['c', 'fg', [30, 30, 18]], ['c', 'bg', [30, 30, 15]], ['p', 'bg', [30, 30, 0, 30, 20, 55]], ['p', 'fg', [8, 30, 18, 30, 13, 40]]])

button1 = createButton()

g = createGame()

gameLoop(g)

pygame.quit()
sys.exit()
