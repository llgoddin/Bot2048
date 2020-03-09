# Lucas Goddin
# 2048 Bot - 0.1
# Feb 25, 2020

from copy import deepcopy
import time
import pyautogui
from PIL import Image
import PIL

# Fitness Weights
WemptySpace = 5
WlargestTileOutOfCorner = -512


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


def simMove(board, direction):
    xDirec = 0
    yDirec = 0

    start = 0
    end = 0
    iterator = 0

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

    for i in range(start, end + xDirec, iterator):
        for j in range(start, end + yDirec, iterator):
            if board[i + yDirec][j + xDirec] == 0:
                board[i + yDirec][j + xDirec] = board[i][j]
                board[i][j] = 0
            elif board[i + yDirec][j + xDirec] == board[i][j]:
                board[i + yDirec][j + xDirec] *= 2
                board[i][j] = 0


screen = pyautogui.screenshot()
greyScreen = screen.convert('L')
gsWidth, gsHeight = greyScreen.size

tileCoordinates = [[(0, 0) for i in range(4)] for j in range(4)]

# Coordinate Info
yOffset = 340
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

# translates grey values into actual values
boardValues = decodeGreyValues(tileGreyValue)

for i in range(4):
    for j in range(4):
        print(boardValues[i][j], end=', ')
    print('\n', end='')

print('\n')
simMove(boardValues, 'l')

for i in range(4):
    for j in range(4):
        print(boardValues[i][j], end=', ')
    print('\n', end='')
