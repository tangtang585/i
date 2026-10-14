# Pixel Grove

A small Python pixel art game. Explore the forest, collect all **8 golden crystals**, and avoid the roaming pink slimes. You have three hearts and a short period of protection after getting hit.

All art is drawn from pixels in code — no image downloads or assets needed.

## Run

Requires Python 3.9+ and a desktop display (Windows, macOS, or Linux).

```sh
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python game.py
```

## Controls

| Key | Action |
| --- | --- |
| Space | Start |
| W / A / S / D | Move up / left / down / right |
| R | Restart |
| Esc | Quit |

The game uses a 320 × 240 pixel canvas scaled to a 960 × 720 window. Resize the window to change the scale; whole-number scaling keeps the artwork crisp.

## Check gameplay logic

```sh
python -m unittest discover -s tests -v
```
