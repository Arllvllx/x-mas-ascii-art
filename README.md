# A Little Winter Wish

A cozy, interactive Christmas desk companion: a rotating 3D-projected ASCII tree, falling snow, twinkling lights, a typewriter greeting, and a focus/countdown timer. It keeps the original winter-night spirit, hand-built pine glyphs, and shooting-star “wish” interaction while rendering in a flicker-free Pygame window.

## Install

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

## Modes and options

```bash
python main.py --mode showcase
python main.py --mode focus --focus 25 --break 5
python main.py --mode countdown --target 2026-12-25
python main.py --message "HAPPY HOLIDAYS" --theme frost --fps 60
python main.py --theme "Frost Blue" --grid-width 96 --grid-height 80
python main.py --fullscreen
python main.py --headless-test
```

`--mode` accepts `showcase`, `focus`, or `countdown`. `--theme` accepts `classic`, `frost`, `neon`, or `warm`, as well as their display names. The character grid defaults to 88×74; `--grid-width` and `--grid-height` configure it. Countdown defaults to Christmas Day, then New Year after December 25; `--target` selects a date. `--headless-test` renders two frames using SDL's dummy display driver and exits.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `1` / `2` / `3` | Showcase / focus timer / holiday countdown |
| `Space` | Pause or resume rotation and timer |
| `F` | Toggle fullscreen |
| `R` | Restart the current animation or focus session |
| `[` / `]` | Shorten or lengthen focus duration by one minute |
| `T` | Cycle Classic Pine, Frost Blue, Cyberpunk Neon, and Warm Gold |
| `S` | Save a timestamped PNG in `exports/` |
| `M` | Toggle sound; enabling it plays a test chime. A chime also plays when a focus session completes. |
| `W` | Send a shooting-star wish |
| `Esc` | Quit |

Run the logic tests with `python -m pytest`.
