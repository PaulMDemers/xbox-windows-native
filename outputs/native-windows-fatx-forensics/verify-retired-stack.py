"""Replay the candidate's complete patch list into an isolated index, without changing sources."""
import hashlib,json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-fatx-forensics';manifest=k/'patch-check-0088.json'
r=json.loads(manifest.read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
with tempfile.TemporaryDirectory() as t:
    env=dict(os.environ,GIT_INDEX_FILE=t+'/index')
    git('read-tree',r['base_commit'],env=env)
    for patch in r['patches']:git('apply','--cached',str(ws/patch),env=env)
    tree=git('write-tree',env=env).decode().strip()
assert tree==r['result_tree']
assert not git('diff','--name-only',tree).strip()
git('diff','--check',r['previous_tree'])
result=dict(scope=__doc__,manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
            patches=len(r['patches']),result_tree=tree,source_matches=True,passed=True)
(k/'retired-replay.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
