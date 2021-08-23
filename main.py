from asciiGraphics import *
from gameManagment import *
from operations import *
import os
import webbrowser


def promptYN(x, y, prompt):
    cmd = None

    while cmd is None:
        setPos(x, y)
        cmd = input(prompt + ' (Y/N): ')

        if cmd.lower() == 'y' or cmd.lower() == 'n':
            return cmd.lower()
        else:
            cmd = None


if __name__ == '__main__':
    # flags
    mainMenuFlag = True
    gameFlag = False
    sessionFlag = False
    createFlag = False
    replayFlag = False

    running = True

    while running:
        # ------------- Menu ---------------------

        while mainMenuFlag:

            loadScreen('screens/mainMenu.txt')

            setPos(44, 25)

            cmd = input()

            if cmd == 'q':
                running = False
                break
            elif cmd == 'p':
                gameFlag = True
                mainMenuFlag = False
                break
            elif cmd == 'a':
                sessionFlag = True
                mainMenuFlag = False
                break

        # ------------- Play Game ---------------------
        if gameFlag:
            game = createGame()
            # Set test board
            # game['board'] = [[8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8]]

            loadScreen('screens/play.txt')

        while gameFlag:
            setPos(2, 10, '  Score: ' + str(game['score']))
            printBoard(game['board'])

            cmd = input('Enter Move: ')

            if cmd == 'q':
                gameFlag = False
                mainMenuFlag = True
                break
            else:
                game['move'] = cmd
                move(game)
                lost = checkGameLost(game)

        # ------------- Session Menu ---------------------
        while sessionFlag:
            loadScreen('screens/sessionMenu.txt')

            setPos(43, 31)

            cmd = input().lower()

            if cmd == 'q':
                sessionFlag = False
                mainMenuFlag = True
                break
            elif cmd == 'c':
                createFlag = True
                break
            elif cmd == 'r':
                replayFlag = True
                break

        # ------------- Replay Menu ---------------------
        while replayFlag:
            loadScreen('screens/replayMenu.txt')

            sessionID = None
            gameID = None
            replayData = None
            replayActive = False
            i = 0

            while sessionID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                setPos(8, 16, 'Session ID:        ')
                setPos(8, 18, '   Game ID:        ')
                setPos(20, 16)

                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    gameID = 0
                    break

                try:
                    cmd = int(cmd)

                    if checkForLog(Session=cmd):
                        sessionID = cmd
                    else:
                        setPos(0, 39, 'Session Not Found')
                except:
                    setPos(0, 39, 'Invalid Input    ')

            while gameID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                setPos(8, 16, 'Session ID: ' + str(sessionID) + '       ')
                setPos(8, 18, '   Game ID:        ')
                setPos(20, 18)

                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    break

                try:
                    cmd = int(cmd)

                    if checkForLog(Session=sessionID, Game=cmd):
                        gameID = cmd
                        replayActive = True
                        replayData = loadReplay(Session=sessionID, Game=gameID)
                    else:
                        setPos(0, 39, 'Game Not Found')
                except:
                    setPos(0, 39, 'Invalid Input')

            while replayActive:
                loadScreen('screens/play.txt')

                printBoard(getReplayBoard(i, replayData), replay=True)

                setPos(3, 11, '----- Game Info ------')
                setPos(3, 13, '      Move #: ' + str(i) +
                       '/' + str(len(replayData.index) - 1))
                setPos(3, 14, '  Game Score: ' + str(replayData['score'][i]))
                setPos(3, 17, '----- Agent Info -----')
                setPos(3, 19, '   Next Move: ' + str(replayData['move'][i]))
                setPos(3, 20, '  Move Score: ' +
                       str(replayData['totalScore'][i]))
                setPos(3, 21, '    Max Tile: ' +
                       str(replayData['maxTileScore'][i]))
                setPos(3, 22, '       Combo: ' +
                       str(replayData['comboScore'][i]))
                setPos(3, 23, 'Corner Stack: ' +
                       str(replayData['cornerStackScore'][i]))

                setPos(8, 30, 'Command: ')

                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    break
                elif cmd == 'd' and i < len(replayData.index) - 1:
                    i += 1
                elif cmd == 'a' and i >= 0:
                    i -= 1
                else:
                    try:
                        cmd = int(cmd)

                        if 0 <= cmd < len(replayData.index):
                            i = cmd
                        else:
                            setPos(0, 39, 'Invalid Move Number')

                    except:
                        setPos(0, 39, 'Invalid Input')

        # ------------- Create Session Menu ---------------------
        while createFlag:
            loadScreen('screens/createSession.txt')

            gameCount = 0
            threadCount = 0

            # Get Number of Games
            while gameCount == 0:
                setPos(25, 15)

                cmd = input()

                if cmd == 'q':
                    createFlag = False
                    threadCount = 1
                    break

                try:
                    cmd = int(cmd)
                    gameCount = cmd
                    break
                except:
                    if cmd == 'q':
                        createFlag = False
                        break
                    else:
                        gameCount = 0

            # Get Number of threads
            while threadCount == 0:
                setPos(27, 17)

                cmd = input()

                try:
                    cmd = int(cmd)
                    if cmd <= 8:
                        threadCount = cmd
                        break
                except:
                    if cmd == 'q':
                        createFlag = False
                        gameCount = 0
                        break
                    else:
                        threadCount = 0

            if gameCount != 0:
                s = createSession(totalGames=gameCount)
                sPath, stats = runSession(s, threads=threadCount)

                printStats(stats)

                stats['Games'] = gameCount
                stats['Threads'] = threadCount

                saveStats(stats)

                qGames = findQuartileGames(sPath)
                graphGames(qGames, sPath, names=['Worst', 'Q1', 'Q2', 'Q3', 'Best'])
                
                cmd = promptYN(8, 28, 'View Graphs?')

                if cmd == 'y':
                    try:
                        filePath = 'file:///' + s['path'] + '/stats.html'
                        webbrowser.open_new_tab(filePath)
                    except:
                        setPos(0, 39, 'Failed To Open File!')

                cmd = promptYN(8, 28, 'Run Another Session?')

                if cmd == 'n':
                    createFlag = False
                    break

    setPos(0, 39, 'Thanks For Playing!\n')
