# python-template

- rename ´src/fun`
- edit `pyproject.toml`
- `make it`


You may want to replace the venv prompt in `.venv/bin/activate` with this:

```sh
# in venv
PROMPT='%F{#808080}rc=%?%f'$'\n\n''%F{blue}%n@%m%f %F{green}%~%f'$'\n''%F{#808080}(.venv) %F{yellow}%#%f '

# out of venv
PROMPT='%F{#808080}rc=%?%f'$'\n\n''%F{blue}%n@%m%f %F{green}%~%f'$'\n''%F{yellow}%#%f '
```