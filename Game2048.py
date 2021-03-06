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

gameScreenButtons = {}
settingsButtons = {}
replayButtons = {}

FPS = 30
fpsClock = pygame.time.Clock()


def replayLoop(gameNum, sessionNum, startingMove=0):
    moves, boards = parseMoveLog(gameNum, sessionNum)

    game = {
        'animationTimer': 10,
        'newTile': (4, 4),
        'moveNum': None,
        'score': None,
        'board': None
    }

    running = True
    index = startingMove

    while running:
        incrementMessage = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        incrementMessage = checkClick(replayButtons, waitForMouseDown=False)

        if incrementMessage == 'replayIncrement':
            index += 1
        elif incrementMessage == 'replayDecrement':
            index -= 1

        game['moveNum'] = index
        game['board'] = boards[index]
        game['score'] = moves[index]

        gameScreenUpdate(game, buttons=replayButtons)


def gameLoop(game):
    waitingToReset = True

    gameScreenUpdate(game, gameScreenButtons)
    while not game['lost']:
        game['move'] = None

        # handle keyboard events while no agent is active
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
            scoreData = None
            game['move'], scoreData = myAlgorithm(game)

        move(game)

        calculateScore(game)

        checkGameLost(game)

        checkClick(gameScreenButtons, game)

        updateAnimation(game)

        gameScreenUpdate(game, gameScreenButtons)

        fpsClock.tick(FPS)

    while waitingToReset:
        for event in pygame.event.get():
            checkClick(gameScreenButtons, game)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        gameScreenUpdate(game, gameScreenButtons)


def settingsLoop(game):
    inSettings = True

    while inSettings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        inSettings = checkClick(settingsButtons, game)
        settingsScreenUpdate(settingsButtons)
        fpsClock.tick(FPS)


def updateAnimation(game):
    # track and update animation
    if game['lost']:
        game['animationTimer'] = 0
        game['newTile'] = (4, 4)
        return None

    if game['newTile'] != (4, 4) and game['animationTimer'] == 0:
        game['animationTimer'] = 1
        return None

    if 0 < game['animationTimer'] < 10:
        game['animationTimer'] += math.floor((11 - game['animationTimer']) / 2)
    elif game['animationTimer'] >= 10:
        game['animationTimer'] = 0
        game['newTile'] = (4, 4)


def gameScreenUpdate(game, buttons):

    screen.fill(LIGHT_GREY)

    # draws title font
    titleText = textRend('2048', 120, DARK_GREY)
    textRect = titleText.get_rect()
    textRect.center = (148, 77)
    screen.blit(titleText, textRect)

    scoreText = None
    if str(game['score']).isnumeric():
        scoreText = textRend('Score: ' + str(game['score']), 30, DARK_GREY)
        scoreTextRect = scoreText.get_rect()
        scoreTextRect.center = (390, 38)
        screen.blit(scoreText, scoreTextRect)
    else:
        scoreText = textRend('Next Move: ' + str(game['score']).upper(), 30, DARK_GREY)
        scoreTextRect = scoreText.get_rect()
        scoreTextRect.center = (390, 38)
        screen.blit(scoreText, scoreTextRect)

        moveText = textRend('Move: ' + str(game['moveNum']), 20, RED)
        moveTextRect = moveText.get_rect()
        moveTextRect.center = (440, 90)
        screen.blit(moveText, moveTextRect)

    mouse = pygame.mouse.get_pos()

    # check buttons to see if they are hovered and change color if they are
    for k, btn in buttons.items():
        if btn['rect'][0] < mouse[0] < btn['rect'][0] + btn['rect'][2]:
            if btn['rect'][1] < mouse[1] < btn['rect'][1] + btn['rect'][3]:
                changeButtonColor(btn, WHITE, GREY)
        else:
            changeButtonColor(btn, WHITE, DARK_GREY)

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

    pygame.display.flip()


def settingsScreenUpdate(buttons):
    screenWidth = pygame.display.get_surface().get_width()
    screenHeight = pygame.display.get_surface().get_height()

    screen.fill(LIGHT_GREY)

    padding = 10
    settingsText = textRend('SETTINGS', 60, DARK_GREY)
    settingsTextRect = settingsText.get_rect()
    settingsTextRect.center = (int(screenWidth / 2), int(settingsTextRect.height / 2) + padding)
    screen.blit(settingsText, settingsTextRect)

    mouse = pygame.mouse.get_pos()

    for k, btn in buttons.items():
        if btn['rect'][0] < mouse[0] < btn['rect'][0] + btn['rect'][2]:
            if btn['rect'][1] < mouse[1] < btn['rect'][1] + btn['rect'][3]:
                changeButtonColor(btn, WHITE, GREY)
        else:
            changeButtonColor(btn, WHITE, DARK_GREY)

    renderButtons(buttons)
    pygame.display.flip()


def textRend(message, size, color):
    font1 = pygame.font.Font('/System/Library/Fonts/AppleSDGothicNeo.ttc', size)
    textObj = font1.render(message, True, color)
    return textObj


def checkClick(btns, game=None, waitForMouseDown=True):
    global mouseDown

    # handle mouse events
    click = pygame.mouse.get_pressed()

    # testing click for 0's makes user let go in between button clicks
    if click == (0, 0, 0):
        mouseDown = False
        return True
    elif click == (1, 0, 0) and (not mouseDown or not waitForMouseDown):
        mouseDown = True
        mouse = pygame.mouse.get_pos()

        # test click to see if it hit any buttons
        for key, btn in btns.items():
            if btn['rect'][0] < mouse[0] < btn['rect'][0] + btn['rect'][2]:
                if btn['rect'][1] < mouse[1] < btn['rect'][1] + btn['rect'][3]:
                    if key == 'newGame':
                        game = createGame(path='NotRecording')
                        gameLoop(game)
                    elif key == 'agent':
                        print('Activating Agent')
                        game['agentActive'] = not game['agentActive']

                        if game['lost']:
                            game = createGame(path='NotRecording')
                            gameLoop(game)
                    elif key == 'settings':
                        settingsLoop(game)
                    elif key == 'back':
                        # TODO fix this back to how its supposed to be
                        # gameLoop(game)
                        replayLoop(00, 18, 200)
                    elif key == 'replayNext':
                        return 'replayIncrement'
                    elif key == 'replayBack':
                        return 'replayDecrement'

    return True


def createButton(rect=[10, 10, 90, 90], text='BTN', fgColor=LIGHT_GREY, bgColor=DARK_GREY, symbol=None):
    btn = {
        'rect': pygame.Rect(rect),
        'text': text,
        'fgColor': fgColor,
        'bgColor': bgColor,
        'symbols': symbol,
        'textSize': None
    }

    return btn


def renderButtons(buttons):
    for k, b in buttons.items():
        pygame.draw.rect(screen, b['bgColor'], b['rect'])

        textObj = None
        if b['text'] is not None:
            textSmallEnough = False
            if b['textSize'] is None:
                textSize = 100
            else:
                textSize = b['textSize']

            textPadding = 8
            while not textSmallEnough:
                textObj = textRend(b['text'], textSize, b['fgColor'])
                textRect = textObj.get_rect()
                if (textRect[2] + textPadding) >= b['rect'][2] or textRect[3] >= b['rect'][3]:
                    textSize -= 1
                    del textObj
                    del textRect
                else:
                    b['textSize'] = textSize
                    textSmallEnough = True

        if b['symbols'] is not None:
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


gameScreenButtons['agent'] = createButton([290, 68, 46, 46], None, WHITE, DARK_GREY,
                                          [['p', 'fg', [7, 7, 7, 39, 39, 23]]])
gameScreenButtons['newGame'] = createButton([344, 68, 46, 46], None, WHITE, DARK_GREY,
                                            [['c', 'fg', [23, 23, 14]],
                                             ['c', 'bg', [23, 23, 12]],
                                             ['p', 'bg', [23, 23, 0, 23, 13, 40]],
                                             ['p', 'fg', [5, 23, 15, 23, 10, 30]]])
gameScreenButtons['settings'] = createButton([398, 68, 75, 46], 'SETTINGS', WHITE, DARK_GREY)

settingsButtons['back'] = createButton([10, 560, 130, 30], '<-- BACK --', WHITE, DARK_GREY)

replayButtons['replayBack'] = createButton([290, 68, 46, 46], None, WHITE, DARK_GREY,
                                          [['p', 'fg', [39, 39, 7, 23, 39, 7]]])
replayButtons['replayNext'] = createButton([344, 68, 46, 46], None, WHITE, DARK_GREY,
                                            [['p', 'fg', [7, 7, 7, 39, 39, 23]]])


g = createGame(path='NotRecording')

gameLoop(g)

pygame.quit()
sys.exit()
