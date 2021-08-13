from gameManagment import *
from asciiGraphics import *
from operations import *
import time

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
    autoFlag = False

    running = True

    while running:
        # ------------- Menu ---------------------

        while True: 

            loadScreen('screens/menu.txt')

            setPos(44, 25)

            cmd = input()

            if cmd == 'q':
                setPos(35, 0)
                running = False
                break
            elif cmd == 'p':
                gameFlag = True
                break
            elif cmd == 'a':
                autoFlag = True
                break
            

        # ------------- Play Game ---------------------

        if gameFlag:
            game = createGame()
            # Set test board
            # game['board'] = [[8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8], [8, 8, 8, 8]]

            loadScreen('screens/play.txt')

        while gameFlag:
            setPos(2, 10, 'Score: ' + str(game['score']))
            printBoard(game['board'])

            cmd = input('Enter Move: ')

            if cmd == 'q':
                gameFlag = False
                break
            else:
                game['move'] = cmd
                move(game)
                lost = checkGameLost(game)


        # ------------- Auto Play Menu ---------------------

        while autoFlag:
            loadScreen('screens/auto.txt')

            gameCount = 0
            threads = 0

            # Get Number of Games
            while gameCount == 0:
                setPos(25, 15)

                cmd = input()

                if cmd == 'q':
                    autoFlag = False
                    threads = 1
                    break

                try:
                    cmd = int(cmd)
                    gameCount = cmd
                    break
                except:
                    if cmd == 'q':
                        autoFlag = False
                        break
                    else:
                        gameCount = 0


            # Get Number of threads
            while threads == 0:
                setPos(27, 17)

                cmd = input()

                try:
                    cmd = int(cmd)
                    if cmd <= 8:
                        threads = cmd
                        break
                except:
                    if cmd == 'q':
                        autoFlag = False
                        gameCount = 0
                        break
                    else:
                        threads = 0

            if gameCount != 0:
                s = createSession(totalGames=gameCount)
                sPath, stats = runSession(s, threads=threads)

                printStats(stats)

                cmd = promptYN(8, 28, 'View Graphs?')

                if cmd == 'y':
                    qGames = findQuartileGames(sPath)

                    graphGames(qGames, sPath, names=['Worst', 'Q1', 'Q2', 'Q3', 'Best'])


                cmd = promptYN(8, 28, 'Run Another Session?')

                if cmd == 'n':
                    autoFlag = False
                    break


    setPos(0, 39, 'Thanks For Playing!\n')
