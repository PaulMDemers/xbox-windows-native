"""Apply and verify this project's recorded ReactOS patch chain."""
import argparse, json, os, pathlib, subprocess, tempfile
p = argparse.ArgumentParser()
p.add_argument('--source', type=pathlib.Path, required=True)
p.add_argument('--manifest', type=pathlib.Path, required=True)
a = p.parse_args()
root = pathlib.Path(__file__).resolve().parent.parent
manifest = json.loads(a.manifest.read_text())
def git(*args, env=None):
    return subprocess.check_output(['git', '-C', str(a.source), *args], env=env)
assert git('rev-parse', 'HEAD').decode().strip() == manifest['base_commit'], 'Wrong upstream commit'
assert not git('status', '--porcelain').strip(), 'Use a clean source checkout'
patches = [(root / n).resolve() for n in manifest['patches']]
assert all(f.is_relative_to(root) and f.is_file() for f in patches)
# Validate the complete series in a temporary index before changing the checkout.
with tempfile.TemporaryDirectory(prefix='xwn-series-') as temp:
    env = dict(os.environ, GIT_INDEX_FILE=str(pathlib.Path(temp) / 'index'))
    git('read-tree', manifest['base_commit'], env=env)
    for patch in patches:
        git('apply', '--cached', str(patch), env=env)
    assert git('write-tree', env=env).decode().strip() == manifest['result_tree']
for patch in patches:
    git('apply', '--index', str(patch))
assert git('write-tree').decode().strip() == manifest['result_tree']
print('Applied and verified source tree ' + manifest['result_tree'])
