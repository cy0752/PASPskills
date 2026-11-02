#!/bin/bash

# Portable entry point; IDs, paths, argv, timeout and concurrency are explicit.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)" || exit 1
exec python3 "$SCRIPT_DIR/method6.py" batch "$@"
