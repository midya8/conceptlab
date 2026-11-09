"""Run outside the checkout against the installed wheel, with fixture paths explicit."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
from conceptlab import audit
root=Path(sys.argv[1]).resolve()
origins={name:str(Path(importlib.import_module(name).__file__).resolve()) for name in ['conceptlab','conceptlab.core','conceptlab.__main__','conceptlab.partial']}
assert all(not Path(p).is_relative_to(root) for p in origins.values()),origins
rows=json.loads((root/'docs/audits.json').read_text())
for row in rows:assert audit(row['input'])==row['report'],row['name']
for command in [['conceptlab'],[sys.executable,'-m','conceptlab']]:
    out=subprocess.check_output(command+[str(root/'examples/demo.json')],text=True)
    assert json.loads(out)==audit(json.loads((root/'examples/demo.json').read_text()))
print(json.dumps({'installed_reports':len(rows),'module_origins':origins,'CLIs':2}))

from conceptlab.partial import audit_partial
partial=json.loads((root/'docs/partial-controls.json').read_text())
expected=json.loads(Path(sys.argv[2]).read_text())
for row,want in zip(partial,expected):
    assert audit_partial(row['input'])==want
assert len(partial)==len(expected)
for command in [['conceptlab'],[sys.executable,'-m','conceptlab']]:
    out=subprocess.check_output(command+['--partial',str(root/'examples/partial.json')],text=True)
    assert json.loads(out)==audit_partial(json.loads((root/'examples/partial.json').read_text()))
print(json.dumps({'installed_partial_reports':len(partial),'partial_CLIs':2}))
