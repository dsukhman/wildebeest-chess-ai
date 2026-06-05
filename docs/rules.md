# Two-player Wildebeest — Piece & Rule Reference

Two-player Wildebeest (2PW) is played on an 11×11 board with a mix of standard chess
pieces and custom ones.

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

Plus standard Pawns, Bishops, Rooks, and Kings. Special board squares (Jet Pack,
Transporter Pads) modify pieces that land on them.

## Board state format

The engine reads a board state from stdin and writes the chosen move to stdout:

```
<turn: W or B>
<11 lines of 11 chars — the grid>
<used_time ms>
<total_time ms>
<move_no>
```

See `examples/board.txt` for a sample starting position.
