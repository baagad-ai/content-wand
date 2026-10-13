#!/bin/sh
# Finds a Python 3 interpreter and runs the content-wand hook dispatcher.
# Exits 0 silently when no interpreter exists: a guard must never break a session.
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for py in python3 python py; do
  if command -v "$py" >/dev/null 2>&1; then
    exec "$py" "$dir/hook_main.py" "$@"
  fi
done
exit 0
