"""A whole session, end to end: create, run, record, analyse, render.

`run_session` is the project's own runner, so these are the tests that say whether
the thing works rather than whether a function does. The one that matters most is
`test_every_recorded_move_replays_legally`: it re-applies every recorded move to
the recorded board and requires the next recorded row to be exactly that board
plus one new 2 or 4. That is the invariant which proves a session on disk is a
real 2048 game and not a by-product of the scorer.

The parallel leg runs in a subprocess deliberately -- see its docstring.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

import pandas as pd

import config
import gameManagment
import Graphing
import InputOutputFunctions
import operations
from tests.helpers import (
    MARKER_COLUMN,
    REPO_ROOT,
    GameTestCase,
    board_from_log_row,
    read_move_log,
)

PARALLEL_SCRIPT = textwrap.dedent('''
    import json, os, sys, tempfile
    repo = sys.argv[1]
    os.chdir(repo)
    sys.path.insert(0, repo)
    import matplotlib
    matplotlib.use("Agg")
    import config
    config.CONFIG["recording_path"] = tempfile.mkdtemp(prefix="bot2048-parallel-")
    import gameManagment
    session = gameManagment.create_session(totalGames=3)
    path, stats = gameManagment.run_session(session, threads=3)
    print(json.dumps({
        "logs": sorted(os.listdir(os.path.join(path, "MoveLogs"))),
        "moves": [game["totalMoves"] for game in session["games"]],
        "lost": [game["lost"] for game in session["games"]],
        "summary": os.path.isfile(os.path.join(path, "gameSummaries.csv")),
    }))
''')


class SessionLayoutTests(GameTestCase):

    def test_a_recorded_session_lays_out_its_directories(self):
        session = gameManagment.create_session(totalGames=4)
        self.assertTrue(os.path.isdir(session['path']))
        self.assertTrue(os.path.isdir(os.path.join(session['path'], 'MoveLogs')))
        self.assertTrue(os.path.isdir(os.path.join(session['path'], 'htmlReportData')))
        self.assertEqual(len(session['games']), 4)

    def test_a_new_session_starts_every_game_with_two_tiles(self):
        session = gameManagment.create_session(totalGames=4)
        for game in session['games']:
            with self.subTest(game=game['id']):
                occupied = sum(1 for row in game['board'] for tile in row if tile != 0)
                self.assertEqual(occupied, 2, 'a new game starts with two tiles')
                self.assertEqual(game['score'], 0)
                self.assertEqual(game['totalMoves'], 0)
                self.assertFalse(game['lost'])

    def test_session_numbering_follows_the_folders_already_there(self):
        first = gameManagment.create_session(totalGames=1)
        second = gameManagment.create_session(totalGames=1)
        self.assertNotEqual(first['path'], second['path'])
        self.assertTrue(second['path'].endswith('Session2'))

    def test_an_unrecorded_session_writes_nothing(self):
        before = sorted(os.listdir(self.recording_dir))
        session = gameManagment.create_session(recording=False, totalGames=2)
        self.assertIsNone(session['path'])
        self.assertEqual(sorted(os.listdir(self.recording_dir)), before)


class SessionRunTests(GameTestCase):
    """One session, run once through the project's own runner and shared."""

    GAMES = 3

    def setUp(self):
        # The session is shared and already written, so keep pointing at it: the
        # per-test temporary directory would hide it from save_stats and load_replay.
        super().setUp()
        config.CONFIG['recording_path'] = self.directory

    @classmethod
    def setUpClass(cls):
        cls._cwd = os.getcwd()
        cls._recording_path = config.CONFIG['recording_path']
        os.chdir(REPO_ROOT)
        cls.directory = tempfile.mkdtemp(prefix='bot2048-session-')
        config.CONFIG['recording_path'] = cls.directory
        cls.session = gameManagment.create_session(totalGames=cls.GAMES)
        cls.path, cls.stats = gameManagment.run_session(cls.session, threads=1)

    @classmethod
    def tearDownClass(cls):
        config.CONFIG['recording_path'] = cls._recording_path
        os.chdir(cls._cwd)
        shutil.rmtree(cls.directory, ignore_errors=True)

    def logs(self):
        folder = os.path.join(self.path, 'MoveLogs')
        return sorted(os.listdir(folder))

    def test_every_game_wrote_a_move_log(self):
        self.assertEqual(self.logs(), [f'game{i}Log.csv' for i in range(self.GAMES)])

    def test_the_games_all_finished(self):
        for game in self.session['games']:
            with self.subTest(game=game['id']):
                self.assertTrue(game['lost'], 'a run session only ends when every game is lost')
                self.assertGreater(game['totalMoves'], 0)

    def test_the_game_was_not_still_in_progress(self):
        self.assertEqual(len(self.session['games']), self.GAMES)

    def test_the_summary_has_one_row_per_game(self):
        summary = pd.read_csv(os.path.join(self.path, 'gameSummaries.csv'))
        self.assertEqual(len(summary.index), self.GAMES)
        self.assertEqual(list(summary.columns),
                         ['Game ID', 'Max Tile', 'Score', 'Total Moves'])

    def test_the_summary_score_is_the_score_at_the_end_of_the_move_log(self):
        summary = pd.read_csv(os.path.join(self.path, 'gameSummaries.csv'))
        for name in self.logs():
            rows = read_move_log(os.path.join(self.path, 'MoveLogs', name))
            game_id = int(name.replace('game', '').replace('Log.csv', ''))
            recorded = int(summary.loc[summary['Game ID'] == game_id, 'Score'].iloc[0])
            with self.subTest(game=game_id):
                self.assertEqual(recorded, int(rows[-1]['score']))

    def test_the_summary_max_tile_is_the_tile_the_final_board_holds(self):
        summary = pd.read_csv(os.path.join(self.path, 'gameSummaries.csv'))
        for name in self.logs():
            rows = read_move_log(os.path.join(self.path, 'MoveLogs', name))
            game_id = int(name.replace('game', '').replace('Log.csv', ''))
            highest = max(tile for row in board_from_log_row(rows[-1]) for tile in row)
            with self.subTest(game=game_id):
                self.assertEqual(int(summary.loc[summary['Game ID'] == game_id, 'Max Tile'].iloc[0]),
                                 highest)

    def test_the_last_row_of_each_log_is_marked_lost(self):
        for name in self.logs():
            rows = read_move_log(os.path.join(self.path, 'MoveLogs', name))
            with self.subTest(log=name):
                self.assertEqual(rows[-1][MARKER_COLUMN], 'l')

    def test_every_recorded_move_replays_legally(self):
        """The invariant behind the whole corpus.

        Applying each recorded move to the recorded board, with tile generation
        off, must reproduce the next recorded row exactly -- plus a single new 2
        or 4 on a cell that was empty. If a move were mis-recorded, or the agent
        scored a board it never played, this is where it shows.
        """
        checked = 0
        for name in self.logs():
            rows = read_move_log(os.path.join(self.path, 'MoveLogs', name))
            for index in range(len(rows) - 1):
                board = board_from_log_row(rows[index])
                following = board_from_log_row(rows[index + 1])
                game = {'id': 0, 'board': [row[:] for row in board],
                        'move': rows[index]['move'], 'totalMoves': 0, 'lost': False}
                operations.move(game, newTile=False)

                differences = [(r, c) for r in range(4) for c in range(4)
                               if game['board'][r][c] != following[r][c]]
                with self.subTest(log=name, move=index):
                    self.assertEqual(len(differences), 1,
                                     f'expected exactly one new tile, got {differences}')
                    row, column = differences[0]
                    self.assertEqual(game['board'][row][column], 0,
                                     'the new tile must land on an empty cell')
                    self.assertIn(following[row][column], (2, 4))
                checked += 1
        self.assertGreater(checked, self.GAMES * 10, 'suspiciously little to check')

    def test_the_stats_describe_the_session(self):
        self.assertEqual(self.stats['ID'], '1')
        self.assertIn('Total Time', self.stats)
        self.assertIn('Average Score', self.stats)
        self.assertIn('Best Game', self.stats)
        for key in ('128', '256', '512', '1024', '2048', '4096'):
            with self.subTest(key=key):
                self.assertGreaterEqual(self.stats[key], 0.0)
                self.assertLessEqual(self.stats[key], 1.0)

    def test_the_report_renders_with_its_charts(self):
        InputOutputFunctions.save_stats(self.stats)
        quartiles = Graphing.find_quartile_games(self.path)
        self.assertEqual(len(quartiles), 5)
        Graphing.graph_games(quartiles, self.path,
                             names=['Worst', 'Q1', 'Q2', 'Q3', 'Best'])

        html = os.path.join(self.path, 'stats.html')
        charts = os.path.join(self.path, 'htmlReportData')
        self.assertGreater(os.path.getsize(html), 0)
        for name in ('Worst', 'Q1', 'Q2', 'Q3', 'Best'):
            with self.subTest(chart=name):
                self.assertTrue(os.path.isfile(os.path.join(charts, name + '.png')))
        self.assertTrue(os.path.isfile(os.path.join(charts, 'style.css')))
        with open(os.path.join(charts, 'sessionStats.json')) as handle:
            self.assertEqual(json.load(handle)['ID'], '1')

    def test_each_game_can_be_replayed_from_its_log(self):
        data = InputOutputFunctions.load_replay(Session=1, Game=0)
        board = InputOutputFunctions.get_replay_board(0, data)
        self.assertEqual(len(board), 4)
        self.assertTrue(all(len(row) == 4 for row in board))
        rows = read_move_log(os.path.join(self.path, 'MoveLogs', 'game0Log.csv'))
        self.assertEqual(len(data.index), len(rows))


class ParallelSessionTests(GameTestCase):

    def test_a_multithreaded_session_runs(self):
        """Run in a subprocess, on purpose.

        `run_session(threads>1)` uses `multiprocessing.Pool`, and Python's spawn
        start method re-imports the parent's `__main__`. Inside a unittest run that
        is the test runner itself, so calling the parallel path from here can
        re-enter discovery. A `python -c` child has no `__main__` file to
        re-import, which makes this a faithful test of the parallel path without
        that hazard. MPLBACKEND is set so the pooled grandchildren pick the
        headless backend too.
        """
        result = subprocess.run(
            [sys.executable, '-c', PARALLEL_SCRIPT, REPO_ROOT],
            capture_output=True, text=True,
            env={**os.environ, 'MPLBACKEND': 'Agg'})
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(payload['logs'], ['game0Log.csv', 'game1Log.csv', 'game2Log.csv'])
        self.assertEqual(len(payload['moves']), 3)
        self.assertTrue(all(moves > 0 for moves in payload['moves']), payload['moves'])
        self.assertTrue(all(payload['lost']), payload['lost'])
        self.assertTrue(payload['summary'])


if __name__ == '__main__':
    unittest.main()
