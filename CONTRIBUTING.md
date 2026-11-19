# Contributing

Terminal 2048 is a small project and the process is small with it. This file says what a change should look like; the [readme](readme.md) says how to run the thing.

## Setting up

- **Python 3.9.** `requirements.txt` is pinned to the versions verified on 3.9.6, which is what CI uses.
- **A virtualenv.** `.env/` is gitignored.

    >$python3 -m venv .env
    >$./.env/bin/pip install -r requirements.txt

- **Run from the repository root.** The project reads `config.json` from the working directory and creates it on first run, and the report writer reads `./templates`.

## Making a change

1. **Branch off `dev`.** `master` is the released baseline and only moves when a version ships, so a pull request opened against it will be asked to retarget.
2. **One concern per commit**, lowercase conventional prefix, one line — `fix: …`, `chore: …`, `docs: …`, `test: …`.
3. **Open a pull request against `dev`**, small and focused. A large change is worth an issue first.
4. **Both gates must be green before review is requested.** They run on every pull request:

    >$python3 -m unittest discover -s tests -t .
    >$ruff check .

The suite is the standard library's `unittest` and needs nothing beyond `requirements.txt`. `ruff` is **not** a project dependency — install it separately (`pip install ruff==0.17.5`, the version CI pins) or let CI run it.

## Tests

A change in behaviour needs a test that fails without it. Two things the suite already guarantees: it pins the direction keys to the shipped `w`/`a`/`s`/`d`, so a rebound `config.json` cannot fail an unrelated test, and it runs against a temporary recording directory, so it never reads or writes your own `game_recordings/`.

Where the code has a known gap, mark the test `expectedFailure` with a note rather than writing it to bless the gap — then remove the marker once the gap is closed.

## Style

`pyproject.toml` holds the rule set, the 88-column line length, and the reason `ruff` was chosen over a style-only checker. The rules deliberately **not** enabled are named there too, so a missing check reads as a decision rather than an oversight.

## Licence

Contributions are accepted under the repository's [MIT licence](LICENSE).
