# Wildebeest Chess AI

A game-playing engine for **Two-player Wildebeest (2PW)**, an 11×11 chess variant featuring serpents, gorillas, catapults, beekeepers, jet-pack kings, and a grand empress that can only be summoned through poison.

The engine uses **alpha-beta search with iterative deepening**, time-aware move selection, and a stack of standard performance tricks (transposition table, Zobrist hashing, killer-move heuristic, evaluation cache, quiescence search).

## The game

Two-player Wildebeest is played on an 11×11 board with a mix of standard chess pieces and custom ones:

| Piece | Behavior |
|---|---|
| **Serpent** | Moves like a king; poisons all adjacent enemies as an after-effect. |
| **Old Woman** | Moves like a king; if a Serpent poisons a piece adjacent to her, she transforms into the Grand Empress and the Serpent dies. |
| **Grand Empress** | Moves like a Queen + Knight + Serpent. Only created via the Old Woman transformation. |
| **Catapult** | Flings adjacent friendly pieces in a straight line over other pieces. |
| **Gorilla** | Cannot be captured; pushes adjacent pieces one square, capturing whatever is behind them. |
| **Beekeeper** | Paralyzes all adjacent enemy pieces. |
| **Prince Joey** | King-like, with a special after-effect rule. |
| **Golf Cart** | Only moves along the top and bottom rows; can rampage. |
| **Time Machine** | Created when a Pawn promotes; charges the Golf Cart. |
| **King with Jet Pack** | What a King becomes after landing on the central Jet Pack square — moves like a Bishop. |

Plus standard Pawns, Bishops, Rooks, and Kings. Special board squares (Jet Pack, Transporter Pads) modify pieces that land on them.

## Engine

- **Search:** alpha-beta with iterative deepening, bounded by the per-move time budget read from the input board state.
- **Move ordering:** killer-move heuristic to improve pruning.
- **Transposition table** keyed by Zobrist hash.
- **Evaluation cache** to avoid recomputing static evaluations.
- **Quiescence search** extends tactical lines past the nominal depth to avoid horizon effects.
- **Evaluation:** material with explosion-aware adjustments (catapults and gorillas can take out clusters), king safety dominant.

## Usage

The engine reads a board state from stdin and writes the chosen move to stdout.
Install it once (editable), then invoke it as the `wildebeest` command or as a module.

```
python -m pip install -e .
```

**Linux/macOS:**
```
wildebeest < examples/board.txt
# or, without the console script:
python -m wildebeest < examples/board.txt
```

**Windows (PowerShell):**
```
Get-Content examples\board.txt | wildebeest
# or:
Get-Content examples\board.txt | python -m wildebeest
```

## Project layout

```
src/wildebeest/         # the engine package
  __main__.py           # enables `python -m wildebeest`
  run.py                # main(): time management + iterative deepening loop
  ai.py                 # alpha-beta search, evaluation, Zobrist, TT, killer moves
  moves.py              # legal move generation for all piece types
  effects.py            # after-effects (poison, promotion, gorilla push, rampage, ...)
  board.py              # board representation, parsing, serialization
  constants.py          # board size, piece codes, directions
  utils.py              # helpers
tests/                  # pytest suite (run with `python -m pytest`)
examples/board.txt      # sample board state
docs/rules.md           # piece & rule reference
```

## Development

```
python -m pip install -e ".[dev]"   # install with pytest
python -m pytest                    # run the test suite
```

## Running under PyPy (faster, optional)

The engine is pure Python with no C-extension dependencies, so it runs unchanged under [PyPy](https://www.pypy.org/), a Python interpreter with a JIT compiler. For this kind of search-heavy code that means a large speedup (commonly 5–30×) with **no code changes**: same source, same moves, just faster.

PyPy keeps its own packages separate from CPython, so the steps are: install PyPy, give it `pip`, install this project into it, then run. After installing PyPy, **open a new terminal** so `pypy3` is on your PATH.

**Linux/macOS:**
```
# install PyPy (e.g. macOS: `brew install pypy3`; Linux: `apt install pypy3`)
pypy3 -m ensurepip            # one-time: bootstrap pip into PyPy
pypy3 -m pip install -e .     # install this project into PyPy
pypy3 -m wildebeest < examples/board.txt
```

**Windows (PowerShell):**
```
# install PyPy (e.g. `winget install PyPy.PyPy.3.11`), then open a new terminal
pypy3 -m ensurepip            # one-time: bootstrap pip into PyPy
pypy3 -m pip install -e .     # install this project into PyPy
Get-Content examples\board.txt | pypy3 -m wildebeest
```

Trade-off: PyPy's JIT needs ~0.5–1s to warm up, so for very short per-move time budgets the benefit is smaller; for multi-second searches it is a clear win.