#!/usr/bin/env python3

import shutil
import subprocess as subproc
import tempfile
from itertools import chain
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROOT = ROOT.resolve()
CHECKSUMS = ROOT / 'sums.md5'
CMDS = ROOT / '.rshsync'


def iter_hashes():
    _cmd = f'md5sum -c {str(CHECKSUMS)}'
    proc = subproc.run(_cmd.split(), capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    for l in lines:
        file, status = l.split(':')
        file = file.strip()
        status = status.strip()
        file_path = Path(file)
        _changed = status == 'FAILED'
        yield file_path.resolve(), _changed


def update_hashes():
    files = list((ROOT / 'src').rglob('**/*.py')) + list((ROOT / 'src').rglob('**/*.tpl'))
    files = [str(f.resolve()) for f in files]
    _cmd = f'md5sum {" ".join(files)}'
    proc = subproc.run(_cmd.split(), capture_output=True, text=True)
    print(proc.stdout)
    proc.check_returncode()
    CHECKSUMS.write_text(proc.stdout)


def iter_pyb_paths(*paths):
    for path in paths:
        rel_path = path.relative_to(ROOT)
        pyb_path = Path('/pyboard').joinpath(*rel_path.parts[1:])
        yield rel_path, pyb_path

def exec_rshell(*args):
    _args = ['rshell', *args] 
    proc = subproc.run(_args)
    proc.check_returncode()

def sync_changed():
    changed = [f for f, changed in iter_hashes() if changed]
    if not any(changed):
        print('No changes found!')
        return
    changed_names = [i.parts for i in changed]
    changed_names = list(chain.from_iterable(changed_names))
    with tempfile.TemporaryDirectory() as tempdir:
        _temp = Path(tempdir)
        shutil.copytree((ROOT / 'src'), str((_temp / 'src')), ignore=lambda src, names: [n for n in names if n not in changed_names])
        exec_rshell('rm /pyboard/templates/*.py')
        _cmd = f'rshell rsync {(_temp / "src")}/ /pyboard/'
        print(_cmd)
        subproc.run(['tree', str(_temp)])
        subproc.run(_cmd.split()).check_returncode()
    update_hashes()
    _cmd = f'rshell repl ~ import main ~ main.main()'
    subproc.run(_cmd.split())


if __name__ == '__main__':
    sync_changed()
