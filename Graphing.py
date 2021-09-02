# Lucas Goddin
# July 6, 2020

import json
from os import mkdir, path

import matplotlib.pyplot as plt
import pandas as pd

with open('config.json') as config_file:
    config = json.load(config_file)


def graph_game_scores(gameID, sessionID, name):
    """Creates and saves game figures to /htmlReportData"""
    
    SESSION_PATH = path.join(config['recording_path'], f'Session{sessionID}')
    HTML_REPORT_PATH = path.join(SESSION_PATH, 'htmlReportData')
    GAME_DATA_PATH = path.join(SESSION_PATH, 'MoveLogs', f'game{gameID}Log.csv')

    
    dfGame = pd.read_csv(GAME_DATA_PATH)

    if name is None:
        plt.figure(f'Game {gameID}')
        GRAPH_PATH = path.join(HTML_REPORT_PATH, f'Game{gameID}.png')
    else:
        plt.figure(f'{name} ({gameID}')
        GRAPH_PATH = path.join(HTML_REPORT_PATH, f'{name}.png')

    dfGame['totalScore'].plot()
    dfGame['maxTileScore'].plot()
    dfGame['comboScore'].plot()
    dfGame['cornerStackScore'].plot()
    plt.title(f'Agent Scores (Game {gameID} - Session {sessionID})')
    plt.xlabel('Moves')
    plt.ylabel('Move Scores')
    plt.legend(['Total Score', 'Max In Corner', 'Combo', 'Corner Stack'])

    if not path.isdir(HTML_REPORT_PATH):
        mkdir(HTML_REPORT_PATH)
    plt.savefig(GRAPH_PATH)


def find_quartile_games(sessionPath):
    """Returns list of five game ID's for worst q1-q3 and best games in descending order"""

    df = pd.read_csv(path.join(sessionPath,'gameSummaries.csv'))

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


def graph_games(gameIDs=[], path='/Session1', names=None):
    """Use to graph multiple games by id"""

    sessionID = int(path.split('Session')[1])

    for id in gameIDs:
        name = None
        if names is not None and len(names) >= 1:
            name = names.pop(0)

        graph_game_scores(id, sessionID, name)
