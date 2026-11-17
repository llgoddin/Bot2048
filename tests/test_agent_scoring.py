"""The agent's four scoring criteria, and the move it picks from them.

`Agent.my_algorithm` is a pure function over a plain dict, which is what makes it
worth testing: it is the whole of the project's decision-making, and a change to
it shows up as a different session rather than as a crash.

The centrepiece is `CombinationScoreTests`, which checks `__combo_check` against
an oracle written from the 2048 rules. That test is the reason this suite exists:
the function compared the move against hard-coded letters (`'l'`, `'r'`, `'u'`)
that no caller has ever passed, so its branch was dead and it always answered the
vertical question -- correct by accident for up and down, wrong for left and
right on about 87% of real boards.
"""
import unittest

import Agent
import config
import operations

from tests.helpers import (DIRECTIONS, GameTestCase, expected_combinations, game_with,
                           grid, private, random_boards)

combo_check = private(Agent, '__combo_check')
corner_check = private(Agent, '__corner_check')
map_tile_sizes = private(Agent, '__map_tile_sizes')
check_corner_stacking = private(Agent, '__check_corner_stacking')

HORIZONTAL_PAIR = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
VERTICAL_PAIR = [[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]


def combinations(rows, direction):
    """`__combo_check` as the agent calls it: a move key and a board."""
    return combo_check({'move': config.CONFIG[direction], 'board': grid(rows)})


class CombinationScoreTests(GameTestCase):

    def test_matches_the_rules_of_the_game_for_every_direction(self):
        boards = [HORIZONTAL_PAIR, VERTICAL_PAIR,
                  [[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                  [[4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4]],
                  [[2, 0, 0, 2], [0, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0]]]
        boards += random_boards(150, seed=21)
        for rows in boards:
            for direction in DIRECTIONS:
                with self.subTest(rows=rows, direction=direction):
                    self.assertEqual(combinations(rows, direction),
                                     expected_combinations(rows, direction))

    def test_a_horizontal_pair_can_only_be_captured_horizontally(self):
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Left'), 4)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Right'), 4)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Up'), 0)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Down'), 0)

    def test_a_vertical_pair_can_only_be_captured_vertically(self):
        self.assertEqual(combinations(VERTICAL_PAIR, 'Up'), 4)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Down'), 4)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Left'), 0)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Right'), 0)

    def test_follows_the_direction_keys_the_config_defines(self):
        # The point of the original defect: the answers must be driven by
        # config.json, not by the letters the code happened to name.
        self.rebind(Up='i', Down='k', Left='j', Right='l')
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Left'), 4)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Right'), 4)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Up'), 0)
        self.assertEqual(combinations(HORIZONTAL_PAIR, 'Down'), 0)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Up'), 4)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Down'), 4)
        self.assertEqual(combinations(VERTICAL_PAIR, 'Left'), 0)

    def test_a_full_line_of_fours_is_worth_two_merges_not_one(self):
        board = [[4, 4, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(combinations(board, 'Left'), 16)

    def test_a_board_that_cannot_merge_scores_nothing_in_any_direction(self):
        board = [[2, 4, 8, 16], [32, 64, 128, 256], [512, 1024, 2, 4], [8, 16, 32, 64]]
        for direction in DIRECTIONS:
            with self.subTest(direction=direction):
                self.assertEqual(combinations(board, direction), 0)

    def test_an_empty_board_scores_nothing_in_any_direction(self):
        for direction in DIRECTIONS:
            with self.subTest(direction=direction):
                self.assertEqual(combinations([[0] * 4] * 4, direction), 0)


class CornerTests(GameTestCase):

    def test_the_largest_tile_in_a_corner_is_worth_its_own_value(self):
        board = [[512, 0, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(corner_check(board), 512)

    def test_each_of_the_four_corners_counts(self):
        for row, column in ((0, 0), (0, 3), (3, 0), (3, 3)):
            board = [[0] * 4 for _ in range(4)]
            board[row][column] = 256
            with self.subTest(corner=(row, column)):
                self.assertEqual(corner_check(board), 256)

    def test_a_largest_tile_away_from_every_corner_scores_nothing(self):
        board = [[0, 0, 0, 4], [512, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(corner_check(board), 0)

    def test_the_score_has_a_floor_of_64(self):
        # Every board starts with the largest tile somewhere, so the criterion
        # pays a flat 64 for cornering it even before it is large.
        board = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(corner_check(board), 64)


class TileMapTests(GameTestCase):

    def test_tiles_are_listed_largest_first_with_their_positions(self):
        board = [[2, 0, 0, 0], [0, 8, 0, 0], [0, 0, 0, 4], [0, 0, 0, 0]]
        tile_info = map_tile_sizes({'board': grid(board)})
        self.assertEqual(tile_info['values'], [8, 4, 2])
        self.assertEqual(tile_info['locations'], [[1, 1], [2, 3], [0, 0]])

    def test_an_empty_board_maps_to_nothing(self):
        tile_info = map_tile_sizes({'board': [[0] * 4] * 4})
        self.assertEqual(tile_info['values'], [])
        self.assertEqual(tile_info['locations'], [])


class CornerStackingTests(GameTestCase):

    def test_adjacent_large_tiles_are_worth_the_smaller_of_them(self):
        boards = [
            [[512, 512, 256, 256], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[512, 256, 256, 256], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        ]
        for board in boards:
            with self.subTest(board=board):
                self.assertEqual(check_corner_stacking({'board': grid(board)}), 256)

    def test_large_tiles_kept_apart_are_worth_nothing(self):
        board = [[512, 512, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [256, 256, 0, 0]]
        self.assertEqual(check_corner_stacking({'board': grid(board)}), 0)

    def test_the_two_largest_tiles_side_by_side_score_on_a_two_tile_board(self):
        """The regression test for the grouping loop's off-by-one.

        `__check_corner_stacking` grouped the tiles with
        `for i in range(len(tileInfo['locations']) - 1)`, which never visited the
        last tile in the descending map. A value group made up solely of that tile
        was therefore never created, so a board holding exactly two tiles -- the
        state every game starts in -- scored 0 for corner stacking even with the
        two large tiles side by side. The bound now covers every tile.
        """
        board = [[512, 256, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(check_corner_stacking({'board': grid(board)}), 256)


class AlgorithmTests(GameTestCase):

    def test_it_returns_one_of_the_configured_directions(self):
        game = game_with([[2, 2, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        move, breakdown = Agent.my_algorithm(game)
        self.assertIn(move, [config.CONFIG[name] for name in DIRECTIONS])
        self.assertEqual(len(breakdown), 4)

    def test_it_never_picks_a_move_that_does_nothing_when_another_works(self):
        for rows in random_boards(100, seed=31):
            with self.subTest(rows=rows):
                game = game_with(rows)
                move, _ = Agent.my_algorithm(game)
                probe = game_with(rows, move=move)
                operations.move(probe, newTile=False)
                self.assertNotEqual(probe['board'], grid(rows),
                                    'chose a no-op on a board with a legal move')

    def test_the_breakdown_covers_every_direction_in_replay_mode(self):
        game = game_with([[2, 2, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        breakdown = Agent.my_algorithm(game, replay=True)
        self.assertEqual(set(breakdown), {config.CONFIG[name] for name in DIRECTIONS})

    def test_each_breakdown_entry_totals_its_three_components(self):
        game = game_with([[2, 2, 2, 0], [4, 0, 4, 0], [0, 8, 0, 0], [0, 0, 0, 0]])
        for move, entry in Agent.my_algorithm(game, replay=True).items():
            with self.subTest(move=move):
                if entry == -1:                       # the move changes nothing
                    continue
                total, high_tile, combo, corner_stack = entry
                self.assertEqual(total, high_tile + combo + corner_stack)

    def test_a_move_that_changes_nothing_is_marked_minus_one(self):
        # The left column is full and cannot move up, so up is a no-op here.
        board = [[2, 4, 0, 0], [16, 8, 0, 0], [32, 16, 0, 0], [64, 32, 0, 0]]
        game = game_with(board)
        breakdown = Agent.my_algorithm(game, replay=True)
        self.assertEqual(breakdown[config.CONFIG['Up']], -1)

    def test_it_is_deterministic(self):
        board = [[2, 2, 4, 0], [8, 0, 8, 0], [0, 16, 0, 0], [0, 0, 2, 0]]
        first = Agent.my_algorithm(game_with(board))
        second = Agent.my_algorithm(game_with(board))
        self.assertEqual(first, second)

    def test_it_does_not_touch_the_board_it_is_asked_about(self):
        # The replay screen re-scores a stored board and then shows it, so a
        # mutation here would corrupt what the user is looking at.
        board = [[2, 2, 4, 0], [8, 0, 8, 0], [0, 16, 0, 0], [0, 0, 2, 0]]
        game = game_with(board)
        before = [row[:] for row in game['board']]
        move_before = game['move']
        Agent.my_algorithm(game)
        Agent.my_algorithm(game, replay=True)
        self.assertEqual(game['board'], before)
        self.assertEqual(game['move'], move_before)

    def test_it_follows_a_rebound_key_configuration(self):
        self.rebind(Up='i', Down='k', Left='j', Right='l')
        game = game_with([[2, 2, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        move, _ = Agent.my_algorithm(game)
        self.assertIn(move, ['i', 'j', 'k', 'l'])


if __name__ == '__main__':
    unittest.main()
