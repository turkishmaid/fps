# FPS

Welche Framerate Limits setzt uns das Terminal?

```
% uv run src/bin/fps.py --help
usage: fps.py [-h] [{w,c}] [color_percent]

FPS Terminal Pattern Display

positional arguments:
  {w,c}          Pattern mode: 'w' for words (default), 'c' for characters
  color_percent  Color percentage for word mode (default: 20.0)

options:
  -h, --help     show this help message and exit
```


&nbsp;

## Setup

```sh
make it
```

You may want to replace the venv prompt in `.venv/bin/activate` with this:

```sh
# in venv
PROMPT='%F{#808080}rc=%?%f'$'\n\n''%F{blue}%n@%m%f %F{green}%~%f'$'\n''%F{#808080}(.venv) %F{yellow}%#%f '

# out of venv
PROMPT='%F{#808080}rc=%?%f'$'\n\n''%F{blue}%n@%m%f %F{green}%~%f'$'\n''%F{yellow}%#%f '
```