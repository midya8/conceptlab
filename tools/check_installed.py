"""Run the complete Python suite and retained CLI reports from a built wheel."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV.pop('PYTHONPATH', None)
MODULES = ['conceptlab', 'conceptlab.__main__', 'conceptlab.core',
           'conceptlab.partial', 'conceptlab.exploration',
           'conceptlab.exploration_verify']


def call(args, cwd):
    return subprocess.check_output(args, cwd=cwd, env=ENV, text=True)


with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    wheels = work / 'wheels'
    wheels.mkdir()
    call([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '-w', str(wheels), str(ROOT)], work)
    venv.create(work / 'env', with_pip=True)
    py = str(work / 'env/bin/python')
    call([py, '-m', 'pip', 'install', '--no-deps', str(next(wheels.glob('*.whl')))], work)
    outside = work / 'outside'
    outside.mkdir()
    for name in ['tests', 'examples', 'docs']:
        shutil.copytree(ROOT / name, outside / name)
    suite = '''
import importlib,importlib.util,json,pathlib,sys,unittest
names=json.loads(sys.argv[1])
for name in names:
    if name!='conceptlab.__main__':importlib.import_module(name)
def check():
    for name in names:
        origin=pathlib.Path(importlib.util.find_spec(name).origin).resolve()
        assert 'site-packages' in origin.parts,(name,str(origin))
check()
suite=unittest.defaultTestLoader.discover(str(pathlib.Path.cwd()/'tests'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.wasSuccessful()
check()
print(json.dumps(dict(tests=result.testsRun,installed_origins=len(names),checked_before_and_after=True)))
'''
    print(call([py, '-I', '-c', suite, json.dumps(MODULES)], outside))
    # Keep the established full-report and both-entrypoint smoke checks intact.
    expected = call([sys.executable, '-c',
                     'import json;from pathlib import Path;from conceptlab.partial import audit_partial;'
                     'print(json.dumps([audit_partial(x["input"]) for x in '
                     'json.loads(Path("docs/partial-controls.json").read_text())]))'], ROOT)
    (work / 'partial-expected.json').write_text(expected)
    installed_env = ENV.copy()
    installed_env['PATH'] = str(work / 'env/bin') + os.pathsep + installed_env['PATH']
    print(subprocess.check_output([py, '-I', str(ROOT / 'tools/verify_installed.py'),
                                   str(ROOT), str(work / 'partial-expected.json')],
                                  cwd=outside, env=installed_env, text=True))
