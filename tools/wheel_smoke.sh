#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
uv build --wheel --out-dir "$TMP/dist" "$ROOT"
uv venv "$TMP/env"
uv pip install --python "$TMP/env/bin/python" "$TMP"/dist/*.whl
cd "$TMP"
PATH="$TMP/env/bin:$PATH" "$TMP/env/bin/python" "$ROOT/tools/verify_installed.py" "$ROOT"
PATH="$TMP/env/bin:$PATH" conceptlab "$ROOT/examples/demo.json" -o console.json
PATH="$TMP/env/bin:$PATH" python -m conceptlab "$ROOT/examples/demo.json" -o module.json
cmp console.json module.json
printf '%s\n' 'Installed wheel reports, module origins and console/module CLI output passed'
