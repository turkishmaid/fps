SHELL := $(SHELL)

.PHONY: it clean sync

it: local sync

local:
	mkdir -p local

sync:
	uv sync

clean:
	rm -rf .venv
	rm -f uv.lock