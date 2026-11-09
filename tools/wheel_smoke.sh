#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PYTHONPATH="$ROOT" python -c 'import sys,json;from pathlib import Path;from conceptlab.partial import audit_partial;print(json.dumps([audit_partial(x["input"]) for x in json.loads(Path(sys.argv[1]).read_text())]))' "$ROOT/docs/partial-controls.json" > "$TMP/partial-expected.json"
uv build --wheel --out-dir "$TMP/dist" "$ROOT"
uv venv "$TMP/env"
uv pip install --python "$TMP/env/bin/python" "$TMP"/dist/*.whl
cd "$TMP"
PATH="$TMP/env/bin:$PATH" "$TMP/env/bin/python" "$ROOT/tools/verify_installed.py" "$ROOT" "$TMP/partial-expected.json"
PATH="$TMP/env/bin:$PATH" conceptlab "$ROOT/examples/demo.json" -o console.json
PATH="$TMP/env/bin:$PATH" python -m conceptlab "$ROOT/examples/demo.json" -o module.json
cmp console.json module.json
printf '%s\n' 'Installed wheel reports, module origins and console/module CLI output passed'
