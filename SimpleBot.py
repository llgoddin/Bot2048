# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

# TODO LIST
# Finish Game Loop
# Work on Setting up the game independently


from copy import deepcopy
import time
import pygame
import pyautogui
from PIL import Image
import PIL
import sys

# Fitness Weights
WemptySpace = 5
WlargestTileOutOfCorner = -512

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
screen.fill((255, 0, 0))
pygame.display.flip()


def gameLoop(b):

    # used to control the main game loop
    userPlaying = True
    keyRelease = True

    while userPlaying:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                userPlaying = False
            if keyRelease:
                if event.type == pygame.KEYDOWN:
                    keyRelease = False
                    if event.key == pygame.K_UP:
                        simMove(b, 'u')
                    if event.key == pygame.K_DOWN:
                        simMove(b, 'd')
                    if event.key == pygame.K_LEFT:
                        simMove(b, 'l')
                    if event.key == pygame.K_RIGHT:
                        simMove(b, 'r')
                if event.type == pygame.KEYUP:
                    keyRelease = True

        printBoard(b)

    sys.exit()


def decodeGreyValues(GreyValues):
    output = [[0 for i in range(4)] for j in range(4)]
    for i in range(4):
        for j in range(4):
            if GreyValues[i][j] == 229:
                output[i][j] = 2
            if GreyValues[i][j] == 225:
                output[i][j] = 4
            if GreyValues[i][j] == 189:
                output[i][j] = 8
            if GreyValues[i][j] == 171:
                output[i][j] = 16
            if GreyValues[i][j] == 157:
                output[i][j] = 32
            if GreyValues[i][j] == 138:
                output[i][j] = 64
            if GreyValues[i][j] == 206:
                output[i][j] = 128
            if GreyValues[i][j] == 202:
                output[i][j] = 256
            if GreyValues[i][j] == 198:
                output[i][j] = 512
            if GreyValues[i][j] == 195:
                output[i][j] = 0
            if GreyValues[i][j] == 192:
                output[i][j] = 2048
            if GreyValues[i][j] == 58:
                output[i][j] = 4096
    return output


def getBoardValues():
    screen = pyautogui.screenshot()
    greyScreen = screen.convert('L')
    gsWidth, gsHeight = greyScreen.size

    tileCoordinates = [[(0, 0) for i in range(4)] for j in range(4)]

    # Coordinate Info
    yOffset = 320
    xOffset = 100
    distance = 123

    for i in range(4):
        for j in range(4):
            if i == 0:
                y = 518 + yOffset
            elif i == 1:
                y = 638 + yOffset
            elif i == 2:
                y = 759 + yOffset
            else:
                y = 870 + yOffset

            if j == 0:
                x = 153 + xOffset
            elif j == 1:
                x = 273 + xOffset
            elif j == 2:
                x = 397 + xOffset
            else:
                x = 515 + xOffset

            tileCoordinates[i][j] = (x, y)

            # Uncomment below to print tile coordinates
            # print(tileCoordinates[i][j], end=', ')
        # print('\n')
    # print('\n' * 3)

    tileGreyValue = [[0 for i in range(4)] for j in range(4)]

    # Get tiles grey values
    for i in range(4):
        for j in range(4):
            gX, gY = tileCoordinates[i][j]
            tileGreyValue[i][j] = greyScreen.getpixel((gX + (j * distance), gY + (i * distance)))
            greyScreen.putpixel((gX + (j * distance), gY + (i * distance)), 0)
            # Uncomment below to print grey scale values
            # print(tileGreyValue[i][j], end=', ')
        # print('\n')

    # save screenshot for debugging
    greyScreen = greyScreen.save('screen.png')

    return decodeGreyValues(tileGreyValue)


def printBoard(board):
    print('-' * 11)
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end=', ')
        print()

    gridXOffset = 50
    gridYOffset = 200

    for i in range(len(board)):
        for j in range(len(board[i])):
            pygame.draw.rect(screen, colorDict[board[i][j]],
                             (gridXOffset + (100 * j), gridYOffset + (100 * i), 100, 100), 0)
            pygame.display.flip()
            print("SCREEN UPDATE")


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


# retrieves and translates grey values into actual values
boardValues = getBoardValues()

# main game loop
gameLoop(boardValues)

print('Original Board: ')
printBoard(boardValues)

print('\nCombined Values After Right Move: ')
simMove(boardValues, 'u')

printBoard(boardValues)

gameLoop(boardValues)
