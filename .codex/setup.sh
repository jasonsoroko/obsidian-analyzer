#!/usr/bin/env bash
set -euo pipefail

# Ensure uv is available
if ! command -v uv >/dev/null 2>&1; then
    python3 -m pip install --break-system-packages uv
fi

# Install project in editable mode with all dependencies
uv pip install -e .
