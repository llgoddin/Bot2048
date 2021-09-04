import webbrowser
from os import name

from matplotlib.pyplot import table

from asciiGraphics import *
from gameManagment import *
from operations import *

if __name__ == '__main__':
    # flags to control the flow of menus
    mainMenuFlag = True
    gameFlag = False
    sessionFlag = False
    createFlag = False
    replayFlag = False
    graphFlag = False

    running = True

    while running:
        # ------------- Menu ---------------------

        while mainMenuFlag:

            load_screen('screens/mainMenu.txt')

            text_out(44, 25)

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
            game = create_game()
            # Set test board
            # game['board'] = [[8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8]]

            load_screen('screens/play.txt')

        while gameFlag:
            text_out(2, 10, f'  Score: {game["score"]}')
            print_board(game['board'])

            cmd = input('Enter Move: ')

            if cmd == 'q':
                gameFlag = False
                mainMenuFlag = True
                break
            else:
                game['move'] = cmd
                move(game)
                lost = check_game_lost(game)

        # ------------- Session Menu ---------------------
        while sessionFlag:
            load_screen('screens/sessionMenu.txt')

            text_out(43, 31)

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
            elif cmd == 'g':
                graphFlag = True
                break

        # ------------- Replay Menu ---------------------
        while replayFlag:
            load_screen('screens/replayMenu.txt')

            sessionID = None
            gameID = None
            replayData = None
            replayActive = False
            i = 0

            while sessionID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                text_out(8, 16, 'Session ID:        ')
                text_out(8, 18, '   Game ID:        ')
                text_out(20, 16)

                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    gameID = 0
                    break

                try:
                    cmd = int(cmd)

                    if check_for_log(Session=cmd):
                        sessionID = cmd
                    else:
                        text_out(0, 39, 'Session Not Found')
                except:
                    text_out(0, 39, 'Invalid Input    ')

            while gameID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                text_out(8, 16, f'Session ID: {sessionID}       ')
                text_out(8, 18, '   Game ID:        ')
                text_out(20, 18)

                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    break

                try:
                    cmd = int(cmd)

                    if check_for_log(Session=sessionID, Game=cmd):
                        gameID = cmd
                        replayActive = True
                        replayData = load_replay(Session=sessionID, Game=gameID)
                    else:
                        text_out(0, 39, 'Game Not Found')
                except:
                    text_out(0, 39, 'Invalid Input')

            while replayActive:
                load_screen('screens/play.txt')

                print_board(get_replay_board(i, replayData), replay=True)
                print_replay_data(replayData, sID=sessionID,
                                  gID=gameID, moveNum=i)

                text_out(8, 30, 'Command: ')
                cmd = input().lower()

                if cmd == 'q':
                    replayFlag = False
                    break
                elif cmd == 'd' and i < len(replayData.index) - 1:
                    i += 1
                elif cmd == 'a' and i >= 0:
                    i -= 1
                elif cmd == 'm':
                    print_move_data(replayData, sID=sessionID,
                                    gID=gameID, moveNum=i)

                    input()
                else:
                    try:
                        cmd = int(cmd)

                        if 0 <= cmd < len(replayData.index):
                            i = cmd
                        else:
                            text_out(0, 39, 'Invalid Move Number')

                    except:
                        text_out(0, 39, 'Invalid Input')

        # ------------- Create Session Menu ---------------------
        while createFlag:
            load_screen('screens/createSession.txt')

            gameCount = 0
            threadCount = 0

            # Get Number of Games
            while gameCount == 0:
                text_out(25, 15)

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
                text_out(27, 17)

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
                s = create_session(totalGames=gameCount)
                sPath, stats = run_session(s, threads=threadCount)

                print_stats(stats)

                stats['Games'] = gameCount
                stats['Threads'] = threadCount

                save_stats(stats)

                qGames = find_quartile_games(sPath)
                graph_games(qGames, sPath, names=[
                           'Worst', 'Q1', 'Q2', 'Q3', 'Best'])

                cmd = prompt_yes_no(8, 28, 'View Graphs?')

                if cmd == 'y':
                    try:
                        filePath = 'file:///' + s['path'] + '/stats.html'
                        webbrowser.open_new_tab(filePath)
                    except:
                        text_out(0, 39, 'Failed To Open File!')

                cmd = prompt_yes_no(8, 28, 'Run Another Session?')

                if cmd == 'n':
                    createFlag = False
                    break

        # ------------- Graph Menu ---------------------
        while graphFlag:
            load_screen('screens/graphMenu.txt')

            sessionID = None
            gameID = None

            while sessionID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                text_out(8, 16, 'Session ID:        ')
                text_out(8, 18, '   Game ID:        ')
                text_out(20, 16)

                cmd = input().lower()

                if cmd == 'q':
                    graphFlag = False
                    gameID = 0
                    break

                try:
                    cmd = int(cmd)

                    if check_for_log(Session=cmd):
                        sessionID = cmd
                    else:
                        text_out(0, 39, 'Session Not Found')
                except:
                    text_out(0, 39, 'Invalid Input    ')

            while gameID is None:
                # I added extra space to make sure all digits are erased in case of invalid input
                text_out(8, 16, 'Session ID: ' + str(sessionID) + '       ')
                text_out(8, 18, '   Game ID:        ')
                text_out(20, 18)

                cmd = input().lower()

                if cmd == 'q':
                    graphFlag = False
                    break

                try:
                    cmd = int(cmd)

                    if check_for_log(Session=sessionID, Game=cmd):
                        gameID = cmd

                        add_graph(sessionID, gameID)

                        text_out(
                            8, 22, 'Your new graph has been rendered and added to stats.hmtl!')
                        text_out(
                            8, 24, 'Be sure to refresh browser to view changes')

                        cmd = prompt_yes_no(8, 27, 'Graph Another Game?')

                        if cmd == 'n':
                            graphFlag = False
                    else:
                        text_out(0, 39, 'Game Not Found')
                except Exception as e:
                    text_out(0, 38, 'Invalid Input')
                    text_out(0, 41, e)

    text_out(0, 39, 'Thanks For Playing!\n')
