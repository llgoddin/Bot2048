# Lucas Goddin
# July 6, 2020

import pandas as pd
import matplotlib.pyplot as plt


def graphGames(gameIDs=[], sessionID=1):

    for id in gameIDs:
        id = int(id)
        if id < 10:
            id = '0' + str(id).strip()
        graphGameScores(id, sessionID)

    plt.show()


def graphGameScores(gameID, sessionID):
    dfGame = pd.read_csv('/Users/lucasgoddin/Documents/PycharmProjects/GameRecording/Session' + str(sessionID).strip() + '/MoveLogs/MoveScores/scoreLog' + str(gameID).strip() + '.csv')

    plt.figure('Game ' + str(gameID))

    dfGame['Total'].plot()
    dfGame['High Tile'].plot()
    dfGame['Combo'].plot()
    dfGame['Corner Stacking'].plot()
    plt.legend(dfGame.columns)
