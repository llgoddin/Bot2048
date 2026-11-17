"""Shared scaffolding for the Bot2048 test suite.

The suite is the standard library's `unittest`, on purpose -- the reason is
recorded in `readme.md` under "Tests".

Two rules hold for everything here:

* **Nothing touches the recording directory the developer uses.** `config.py`
  reads `recording_path` once at import, but every module binds the same `CONFIG`
  dict through `from config import *`, so repointing that one key (and putting it
  back on the way out) isolates the whole suite.
* **Nothing depends on wall-clock or unseeded randomness.** Tests that need
  random tiles seed `random` themselves, so a failure is always reproducible.
"""
import csv
import os
import random
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import matplotlib

matplotlib.use('Agg')

import config
import operations

DIRECTIONS = ('Up', 'Down', 'Left', 'Right')
BOARD_COLUMNS = [str(i) for i in range(16)]
MARKER_COLUMN = 'Win/Loss/Continue'


class GameTestCase(unittest.TestCase):
    """Base class: repository root as the working directory, throwaway recordings."""

    def setUp(self):
        self._cwd = os.getcwd()
        self._recording_path = config.CONFIG['recording_path']
        self._keys = {name: config.CONFIG[name] for name in DIRECTIONS}
        os.chdir(REPO_ROOT)                     # save_stats reads ./templates
        self.recording_dir = tempfile.mkdtemp(prefix='bot2048-tests-')
        config.CONFIG['recording_path'] = self.recording_dir

    def tearDown(self):
        config.CONFIG.update(self._keys)
        config.CONFIG['recording_path'] = self._recording_path
        os.chdir(self._cwd)
        shutil.rmtree(self.recording_dir, ignore_errors=True)

    def rebind(self, **keys):
        """Repoint the direction keys the way a user's config.json may."""
        config.CONFIG.update(keys)
        return {name: config.CONFIG[name] for name in DIRECTIONS}

    def key(self, direction):
        return config.CONFIG[direction]


def grid(rows):
    """A fresh 4x4 board from four rows of four."""
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise ValueError('a board is four rows of four')
    return [list(row) for row in rows]


def from_flat(flat):
    """A 4x4 board from the flat 16-cell row a move log stores."""
    cells = list(flat)
    return [cells[i * 4:(i + 1) * 4] for i in range(4)]


def game_with(rows, move=None, score=None):
    """A game dict carrying the keys `operations.move` touches."""
    game = {'id': 0, 'board': grid(rows), 'move': move, 'totalMoves': 0, 'lost': False}
    if score is not None:
        game['score'] = score
    return game


def slid(rows, direction, score=None):
    """Apply one move with tile generation off, so the board can be asserted exactly."""
    game = game_with(rows, move=config.CONFIG[direction], score=score)
    operations.move(game, newTile=False)
    return game


def private(module, name):
    """Reach a module-level `__name` without Python's name mangling.

    `__combo_check` is module-level, not a class attribute, so it is reachable --
    but writing `Agent.__combo_check` inside a class body would mangle it into
    `_TheTest__combo_check`. Always go through this.
    """
    return getattr(module, name)


# --------------------------------------------------------------------------
# The oracle: what "available combinations" means, from the 2048 rules alone.
#
# Deliberately written without reading Agent.__combo_check, so agreement between
# the two is evidence rather than a restatement.
# --------------------------------------------------------------------------

def line_merges(line):
    """Points captured when one line of 2048 is pushed: compress, then pair up."""
    tiles = [tile for tile in line if tile != 0]
    score = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            score += tiles[i] * 2
            i += 2
        else:
            i += 1
    return score


def expected_combinations(rows, direction):
    """The points a move in `direction` can capture on this board."""
    if direction in ('Left', 'Right'):
        return sum(line_merges(row) for row in rows)
    return sum(line_merges([rows[r][c] for r in range(4)]) for c in range(4))


def usable(rows):
    """True when the board has at least one legal move."""
    if any(cell == 0 for row in rows for cell in row):
        return True
    if any(rows[r][c] == rows[r][c + 1] for r in range(4) for c in range(3)):
        return True
    return any(rows[r][c] == rows[r + 1][c] for r in range(3) for c in range(4))


def random_boards(count, seed, values=(0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)):
    """A reproducible corpus of boards, including high-tile positions."""
    rng = random.Random(seed)
    boards = []
    while len(boards) < count:
        rows = [[rng.choice(values) for _ in range(4)] for _ in range(4)]
        if usable(rows):
            boards.append(rows)
    return boards


# --------------------------------------------------------------------------
# Reading back what a session wrote.
# --------------------------------------------------------------------------

def read_move_log(path):
    """A move log as a list of dicts, one per recorded decision."""
    with open(path, newline='') as handle:
        return list(csv.DictReader(handle))


def board_from_log_row(row):
    return from_flat([int(row[column]) for column in BOARD_COLUMNS])


def final_board(rows):
    """The board as the log's last row holds it."""
    return rows[-1] if rows else []
