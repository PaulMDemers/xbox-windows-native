"""SPDX-License-Identifier: MIT
Reconstruct one pinned source tree in a NEW directory, without building or deploying.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value: raise ValueError(message)


def load_component(name):
    document = json.loads((ROOT/'components.json').read_text(encoding='utf-8'))
    matches = [x for x in document['components'] if x['name'] == name]
    require(len(matches) == 1, 'Unknown or duplicate component')
    c = matches[0]
    patch = (ROOT/c['patch']).resolve(strict=True)
    require(patch.is_relative_to(ROOT) and patch.suffix == '.patch', 'Patch outside package')
    data = patch.read_bytes()
    require(hashlib.sha256(data).hexdigest() == c['patch_sha256'], 'Patch digest mismatch')
    for key in ('base_commit','result_tree'):
        require(len(c[key]) == 40 and all(x in '0123456789abcdef' for x in c[key]), 'Invalid Git identity')
    return c, patch


def reconstruct(name, cache, output, index_only=False):
    c, patch = load_component(name)
    cache = Path(cache).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists(), 'Output already exists; use a fresh attempt')
    require(not output.is_relative_to(cache) and not cache.is_relative_to(output), 'Output overlaps source cache')
    require(not output.is_relative_to(ROOT), 'Keep generated source outside this package')
    parent = output.parent
    require(parent.is_dir(), 'Create the output parent explicitly first')
    require(shutil.disk_usage(parent).free >= 20*1024**3, '20 GiB free-space reserve required')
    # The caller supplies a local, trusted Git cache. No implicit downloads or alternates.
    subprocess.run(['git','-C',str(cache),'cat-file','-e',c['base_commit']+'^{commit}'],check=True)
    output.mkdir()
    report = {'component':name,'base_commit':c['base_commit'],'expected_tree':c['result_tree'],
              'patch_sha256':c['patch_sha256'],'status':'started','compiled':False,'deployed':False}
    def git(*args):
        return subprocess.check_output(['git','-C',str(output),*args],stderr=subprocess.STDOUT)
    try:
        git('init','-q')
        git('config','core.autocrlf','false')
        git('fetch','--depth=1',str(cache),c['base_commit'])
        git('read-tree',c['base_commit'])
        git('apply','--cached',str(patch))
        actual = git('write-tree').decode().strip()
        require(actual == c['result_tree'], 'Reconstructed tree mismatch')
        if not index_only:
            # checkout-index includes export-ignore files; git archive would omit them.
            git('checkout-index','--all')
        report.update(status='source-verified',actual_tree=actual,working_files_written=not index_only)
    except BaseException as exc:
        report.update(status='failed',error=type(exc).__name__)
        raise
    finally:
        (output/'reconstruction-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--component',required=True)
    p.add_argument('--source-cache',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--index-only',action='store_true',help='Verify source tree without materializing files')
    a = p.parse_args()
    print(json.dumps(reconstruct(a.component,a.source_cache,a.output,a.index_only),indent=2))


if __name__ == '__main__': main()
