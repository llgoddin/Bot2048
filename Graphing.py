# Lucas Goddin
# July 6, 2020

import pandas as pd
import matplotlib.pyplot as plt


def findQuartileGames(sessionPath):
    gameSummariesPath = sessionPath + '/gameSummaries.txt'

    sumFile = open(gameSummariesPath, 'r')

    lines = sumFile.readlines()[3:]

    sumFile.close()

    scoreData = []
    maxTileData = []
    for line in lines:
        statStr = line.split('- ')[1]
        statStr = statStr.split(', ')

        scoreData.append(int(statStr[1]))
        maxTileData.append(int(statStr[0]))

    scoreDf = pd.DataFrame(data=scoreData, columns=['Score'])

    gameInfo = scoreDf.quantile([0.25, 0.5, 0.75])

    print(gameInfo)

    q1MinDist = 500
    q2MinDist = 500
    q3MinDist = 500

    q1Game = 0
    q2Game = 0
    q3Game = 0

    for i in range(len(scoreDf['Score'])):
        if abs(scoreDf['Score'][i] - gameInfo['Score'][0.25]) < q1MinDist:
            q1MinDist = abs(scoreDf['Score'][i] - gameInfo['Score'][0.25])
            q1Game = i

        if abs(scoreDf['Score'][i] - gameInfo['Score'][0.5]) < q2MinDist:
            q1MinDist = abs(scoreDf['Score'][i] - gameInfo['Score'][0.5])
            q2Game = i

        if abs(scoreDf['Score'][i] - gameInfo['Score'][0.75]) < q3MinDist:
            q1MinDist = abs(scoreDf['Score'][i] - gameInfo['Score'][0.75])
            q3Game = i

    plt.figure('Box Plot')

    data = list(zip(scoreData, maxTileData))
    df = pd.DataFrame(data=data, columns=['Scores', 'Max Tile'])
    df.boxplot()

    return [q1Game, q2Game, q3Game]


def graphGames(gameIDs=[], path='/Session1', names=None):
    sessionID = int(path.split('Session')[1])

    for num in gameIDs:
        num = int(num)
        if num < 10:
            numStr = '0' + str(num).strip()
        else:
            numStr = str(num).strip()

        name = None
        if names is not None and len(names) >= 1:
            name = names.pop(0)

        graphGameScores(numStr, sessionID, name)

    plt.show()


def graphGameScores(gameID, sessionID, name):
    dfGame = pd.read_csv('/Users/lucasgoddin/Documents/PycharmProjects/GameRecording/Session' + str(sessionID).strip() + '/MoveLogs/MoveScores/scoreLog' + str(gameID) + '.csv')

    if name is None:
        plt.figure('Game ' + str(gameID))
    else:
        plt.figure(str(name) + ' (' + str(gameID) + ')')

    dfGame['Total'].plot()
    dfGame['High Tile'].plot()
    dfGame['Combo'].plot()
    dfGame['Corner Stacking'].plot()
    plt.legend(dfGame.columns)
