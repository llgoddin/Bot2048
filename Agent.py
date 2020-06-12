from multiprocessing import Pipe
from Game2048 import move, printBoard, readBoard
import copy

# weights
CORNER_BONUS = 100


def start(board, pipe):
    pipe.send('Starting Bot')
    running = True

    while running:
        chosenMove = myAlgorthim(board)
        pipe.send(chosenMove)
        board = pipe.recv()
    pipe.close()


def myAlgorthim(board):
    # I'm going to try applying different weights to game states in order to choose the best move
    # Important things are going to include keeping the largest tiles in the corner

    moves = ['l', 'r', 'u', 'd']
    moveScoresDict = {}

    tempBoard = copy.deepcopy(board)

    for m in moves:
        score = 0
        move(tempBoard, direction=m)

        # calculate score
        score += cornerCheck(tempBoard)
        score += comboCheck(tempBoard)
        move(board, direction=m)
        score += comboCheck(tempBoard)

        moveScoresDict[m] = score
        tempBoard = board
        print('tempBoard reset Values VVV\n' + '-' * 10)
        printBoard(tempBoard)

    bestMove = 'l'
    for m in moves:
        if moveScoresDict[m] > moveScoresDict[bestMove]:
            bestMove = m

    return bestMove


def cornerCheck(board):
    # find the largest tile
    largestTile = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] > largestTile:
                largestTile = board[i][j]

    # check corners for the largest tile
    cornerCoord = [(0, 0), (0, 3), (3, 0), (3, 3)]

    for corner in cornerCoord:
        if board[corner[0]][corner[1]] == largestTile:
            return CORNER_BONUS

    return 0


def comboCheck(board):
    return 0


def sendMove(m):
    print('Best Move is: ' + m)

