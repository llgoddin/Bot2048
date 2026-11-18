"""The 2048 rules themselves: merging, compression and liveness.

These are the tests to run first when the game feels wrong, because every
recorded session rests on them. `operations.move` is the only entry point used --
the private combine step is exercised through it, so the compression pass is
covered at the same time.
"""
import random
import unittest

import config
import operations
from tests.helpers import (
    DIRECTIONS,
    GameTestCase,
    game_with,
    grid,
    random_boards,
    slid,
)

ROWS = [[2, 2, 0, 0], [4, 0, 4, 0], [8, 0, 0, 8], [16, 0, 0, 0]]


def empty_but(row, column, value):
    rows = [[0, 0, 0, 0] for _ in range(4)]
    rows[row][column] = value
    return rows


def mirror(rows):
    return [list(reversed(row)) for row in rows]


def transpose(rows):
    return [[rows[r][c] for r in range(4)] for c in range(4)]


class MergeTests(GameTestCase):

    def test_a_pair_merges_toward_the_wall_and_scores_the_merged_tile(self):
        game = slid([[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [4, 0, 0, 0])
        self.assertEqual(game['score'], 4)

    def test_a_full_row_merges_into_two_tiles(self):
        game = slid([[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [4, 4, 0, 0])
        self.assertEqual(game['score'], 8)

    def test_a_tile_merges_only_once_in_a_move(self):
        # [4,4,4,4] left is [8,8], never [16]: a tile produced by a merge cannot
        # merge again in the same move.
        game = slid([[4, 4, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [8, 8, 0, 0])
        self.assertEqual(game['score'], 16)

    def test_a_pair_merges_across_a_gap(self):
        game = slid([[2, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [4, 0, 0, 0])
        self.assertEqual(game['score'], 4)

    def test_the_nearest_tile_is_the_one_that_pairs(self):
        # left on [2,2,2,0] merges the two leftmost, leaving [4,2,0,0]
        game = slid([[2, 2, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [4, 2, 0, 0])
        self.assertEqual(game['score'], 4)


class CompressionTests(GameTestCase):

    def test_tiles_slide_to_the_wall(self):
        self.assertEqual(slid([[0, 2, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                              'Left')['board'][0], [2, 4, 0, 0])
        self.assertEqual(slid([[0, 2, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                              'Right')['board'][0], [0, 0, 2, 4])

    def test_a_full_row_that_cannot_move_is_a_no_op(self):
        game = slid([[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left', score=0)
        self.assertEqual(game['board'][0], [2, 4, 8, 16])
        self.assertEqual(game['score'], 0)

    def test_a_no_op_move_does_not_count_as_a_move(self):
        game = game_with([[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], move='a')
        before = [row[:] for row in game['board']]
        operations.move(game)                      # newTile defaults on
        self.assertEqual(game['board'], before)
        self.assertEqual(game['totalMoves'], 0)

    def test_down_does_not_wrap_the_bottom_row_to_the_top(self):
        # The compression bounds are subtler than they look: moving down iterates
        # rows 3..1 reading row i-1, so row 0 must never be written.
        game = slid([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]], 'Down', score=0)
        self.assertEqual(game['board'], [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]])
        self.assertEqual(game['score'], 0)

    def test_down_stacks_and_merges_at_the_bottom(self):
        game = slid([[0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0], [2, 0, 0, 0]], 'Down', score=0)
        self.assertEqual(game['board'], [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [4, 0, 0, 0]])
        self.assertEqual(game['score'], 4)

    def test_up_stacks_and_merges_at_the_top(self):
        game = slid([[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Up', score=0)
        self.assertEqual(game['board'], [[4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self.assertEqual(game['score'], 4)


class DirectionSymmetryTests(GameTestCase):
    """A horizontal move on a board is a vertical move on its transpose, and so on.

    Cheap to state, and it catches an axis being swapped or a loop bound being
    off by one in a way a single worked example would not.
    """

    def test_left_mirrors_onto_right(self):
        for rows in random_boards(60, seed=11):
            with self.subTest(rows=rows):
                self.assertEqual(mirror(slid(rows, 'Left')['board']),
                                 slid(mirror(rows), 'Right')['board'])

    def test_up_transposes_onto_left(self):
        for rows in random_boards(60, seed=12):
            with self.subTest(rows=rows):
                self.assertEqual(transpose(slid(rows, 'Up')['board']),
                                 slid(transpose(rows), 'Left')['board'])

    def test_down_transposes_onto_right(self):
        for rows in random_boards(60, seed=13):
            with self.subTest(rows=rows):
                self.assertEqual(transpose(slid(rows, 'Down')['board']),
                                 slid(transpose(rows), 'Right')['board'])

    def test_a_move_never_creates_or_loses_points_of_tile_value(self):
        # merging conserves the sum of tile values: 2+2 -> 4
        for rows in random_boards(60, seed=14):
            for direction in DIRECTIONS:
                with self.subTest(rows=rows, direction=direction):
                    before = sum(sum(row) for row in rows)
                    after = sum(sum(row) for row in slid(rows, direction)['board'])
                    self.assertEqual(before, after)


class InvalidMoveTests(GameTestCase):

    def test_a_direction_outside_the_config_is_ignored(self):
        game = game_with(ROWS, move='z')
        before = [row[:] for row in game['board']]
        self.assertIsNone(operations.move(game))
        self.assertEqual(game['board'], before)

    def test_a_game_with_no_move_yet_is_ignored(self):
        game = game_with(ROWS, move=None)
        before = [row[:] for row in game['board']]
        self.assertIsNone(operations.move(game))
        self.assertEqual(game['board'], before)

    def test_the_direction_keys_are_read_from_the_config(self):
        # 'w'/'a'/'s'/'d' mean nothing once the keys are rebound; the rules must
        # follow config.json rather than the shipped defaults.
        self.rebind(Up='i', Down='k', Left='j', Right='l')
        self.assertIsNone(operations.move(game_with(ROWS, move='a')))
        game = slid([[0, 2, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'Left')
        self.assertEqual(game['board'][0], [2, 4, 0, 0])


class NewTileTests(GameTestCase):

    def test_a_real_move_adds_exactly_one_tile_and_counts_the_move(self):
        random.seed(2)
        game = game_with([[0, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], move='a')
        operations.move(game)
        self.assertEqual(game['totalMoves'], 1)
        filled = [(r, c) for r in range(4) for c in range(4) if game['board'][r][c] != 0]
        self.assertEqual(len(filled), 2)
        row, column = game['newTile']
        self.assertIn(game['board'][row][column], (2, 4))
        self.assertIn((row, column), filled)

    def test_generation_lands_on_an_empty_cell(self):
        random.seed(3)
        rows = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 0]]
        for _ in range(200):
            game = game_with(rows, move='a')
            before = [row[:] for row in game['board']]
            operations.gen_tile(game)
            changed = [(r, c) for r in range(4) for c in range(4)
                       if game['board'][r][c] != before[r][c]]
            self.assertEqual(len(changed), 1)
            self.assertEqual(tuple(game['newTile']), changed[0])
            self.assertEqual(before[changed[0][0]][changed[0][1]], 0)
            self.assertIn(game['board'][changed[0][0]][changed[0][1]], (2, 4))

    def test_a_real_move_adds_exactly_one_tile_on_top_of_the_slide(self):
        # Each direction must change this board, so every leg is a real move.
        rows = [[0, 2, 0, 0], [0, 0, 0, 0], [0, 2, 0, 0], [0, 0, 0, 0]]

        def occupied(cells):
            return sum(1 for line in cells for tile in line if tile != 0)

        for direction in DIRECTIONS:
            with self.subTest(direction=direction):
                slid_only = game_with(rows, move=config.CONFIG[direction])
                operations.move(slid_only, newTile=False)
                self.assertNotEqual(slid_only['board'], grid(rows), 'this leg is a no-op')
                with_tile = game_with(rows, move=config.CONFIG[direction])
                operations.move(with_tile, newTile=True)
                self.assertEqual(occupied(with_tile['board']),
                                 occupied(slid_only['board']) + 1)

    def test_roughly_one_tile_in_ten_is_a_four(self):
        # gen_tile places a 4 when random.random() > 0.9
        random.seed(4)
        fours = 0
        draws = 4000
        for _ in range(draws):
            game = game_with([[0] * 4] * 4, move='a')
            operations.gen_tile(game)
            row, column = game['newTile']
            if game['board'][row][column] == 4:
                fours += 1
        self.assertGreater(fours / draws, 0.08)
        self.assertLess(fours / draws, 0.12)


class LivenessTests(GameTestCase):

    LOCKED = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]

    def test_a_locked_board_is_lost(self):
        game = game_with(self.LOCKED, move='a')
        self.assertTrue(operations.check_game_lost(game))
        self.assertTrue(game['lost'])

    def test_a_board_with_a_merge_left_is_not_lost(self):
        game = game_with([[2, 2, 4, 8], [4, 8, 16, 32], [2, 4, 8, 16], [4, 8, 16, 32]], move='a')
        self.assertFalse(operations.check_game_lost(game))
        self.assertFalse(game['lost'])

    def test_a_board_with_an_empty_cell_is_not_lost(self):
        game = game_with([[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 0]], move='a')
        self.assertFalse(operations.check_game_lost(game))

    def test_liveness_does_not_depend_on_the_move_asked_about(self):
        # check_game_lost tries all four directions itself, so whatever is in
        # game['move'] must not change the answer.
        for move in ('w', 'a', 's', 'd'):
            with self.subTest(move=move):
                game = game_with(self.LOCKED, move=move)
                self.assertTrue(operations.check_game_lost(game))


class ScoreTests(GameTestCase):

    def test_score_is_optional(self):
        game = game_with([[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], move='a')
        self.assertNotIn('score', game)
        operations.move(game, newTile=False)          # must not raise
        self.assertNotIn('score', game)

    def test_score_accumulates_across_moves(self):
        game = game_with([[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                         move='a', score=0)
        operations.move(game, newTile=False)
        self.assertEqual(game['score'], 8)
        game['move'] = 'a'
        operations.move(game, newTile=False)
        self.assertEqual(game['score'], 8)            # nothing left to merge


if __name__ == '__main__':
    unittest.main()
