# Lucas Goddin
# March 5, 2020


def simMove(board, direction):
    xDirec = 0
    yDirec = 0

    if direction == 'l':
        xDirec = -1
    elif direction == 'r':
        xDirec = 1
    elif direction == 'u':
        yDirec = -1
    elif direction == 'd':
        yDirec = 1


boardValues = [[0 for i in range(4)] for j in range(4)]

boardValues = [[0, 0, 0, 0], [2, 0, 2, 4], [8, 8, 4, 4], [16, 0, 2, 0]]
