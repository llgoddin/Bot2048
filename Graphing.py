# Lucas Goddin
# July 6, 2020

from os import mkdir, path
import pandas as pd
import matplotlib.pyplot as plt
import json

with open('config.json') as config_file:
    config = json.load(config_file)


def findQuartileGames(sessionPath):
    df = pd.read_csv(sessionPath + '/gameSummaries.csv')

    gameInfo = df['Score'].quantile([0, 0.25, 0.5, 0.75, 1])

    q1MinDist = 500
    q2MinDist = 500
    q3MinDist = 500

    worst_ID = 0
    best_ID = 0
    q1_ID = 0
    q2_ID = 0
    q3_ID = 0

    for i in range(len(df['Score'])):
        if df['Score'][i] == gameInfo[0]:
            worst_ID = i

        if df['Score'][i] == gameInfo[1]:
            best_ID = i

        if abs(df['Score'][i] - gameInfo[0.25]) < q1MinDist:
            q1MinDist = abs(df['Score'][i] - gameInfo[0.25])
            q1_ID = i

        if abs(df['Score'][i] - gameInfo[0.5]) < q2MinDist:
            q2MinDist = abs(df['Score'][i] - gameInfo[0.5])
            q2_ID = i

        if abs(df['Score'][i] - gameInfo[0.75]) < q3MinDist:
            q3MinDist = abs(df['Score'][i] - gameInfo[0.75])
            q3_ID = i

    plt.figure('Box Plot')

    data = list(zip(df['Score'], df['Max Tile']))
    df = pd.DataFrame(data=data, columns=['Scores', 'Max Tile'])
    df.boxplot()

    return [worst_ID, q1_ID, q2_ID, q3_ID, best_ID]


def graphGames(gameIDs=[], path='/Session1', names=None):
    sessionID = int(path.split('Session')[1])

    for id in gameIDs:
        name = None
        if names is not None and len(names) >= 1:
            name = names.pop(0)

        graphGameScores(id, sessionID, name)


def graphGameScores(gameID, sessionID, name):
    dfGame = pd.read_csv(config['recording_path'] + '/Session' + str(
        sessionID).strip() + '/MoveLogs/game' + str(gameID) + 'Log.csv')

    if name is None:
        plt.figure('Game ' + str(gameID))
    else:
        plt.figure(str(name) + ' (' + str(gameID) + ')')

    dfGame['totalScore'].plot()
    dfGame['maxTileScore'].plot()
    dfGame['comboScore'].plot()
    dfGame['cornerStackScore'].plot()
    plt.title('Agent Scores (' + 'Game ' + str(gameID) +
              ' - Session ' + str(sessionID) + ')')
    plt.xlabel('Moves')
    plt.ylabel('Move Scores')
    plt.legend(['Total Score', 'Max In Corner', 'Combo', 'Corner Stack'])

    if not path.isdir(config['recording_path'] + '/Session' + str(sessionID) + '/htmlReportData'):
        mkdir(config['recording_path'] + '/Session' +
              str(sessionID) + '/htmlReportData')
    plt.savefig(config['recording_path'] + '/Session' +
                str(sessionID) + '/htmlReportData/' + str(name) + '.png')
