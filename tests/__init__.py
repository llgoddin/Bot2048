"""The Bot2048 test package.

Kept importable so `python -m unittest discover -s tests -t .` collects
`tests.test_*` and the repository root stays on `sys.path`, which is what lets
the tests import the top-level modules (`config`, `operations`, `Agent`, ...).
"""
import matplotlib

# The report path imports pyplot. Pick the headless backend before anything can
# import it, so the suite runs the same on a laptop and on a CI runner with no
# display attached.
matplotlib.use('Agg')

import config

# The suite runs against the keys `config.py` ships, not against whatever the
# developer's own `config.json` happens to hold.
#
# `config.json` is gitignored and user-editable, and `config.py` reads it at
# import, so without this pin a rebound arrow key would fail tests that have
# nothing to do with configuration -- which is exactly what happened while this
# suite was being written. The tests that *are* about configuration rebind
# explicitly and `GameTestCase.tearDown` puts them back.
SHIPPED_KEYS = {'Up': 'w', 'Down': 's', 'Left': 'a', 'Right': 'd'}
config.CONFIG.update(SHIPPED_KEYS)
