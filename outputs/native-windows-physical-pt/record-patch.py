import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos');root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=root/'outputs/native-windows-physical-pt'
previous=json.loads((root/'outputs/native-windows-physical-size/patch-check-0034.json').read_text());base=previous['base_commit'];before=previous['result_tree']
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
p=out/'0035-first-page-tables.patch';assert not p.exists();p.write_bytes(git('diff','--binary',before));git('apply','--reverse','--check',str(p));git('diff','--check')
patches=[root/name for name in previous['patches']]+[p]
with tempfile.TemporaryDirectory(prefix='xwn-patch-') as tmp:
 env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index');git('read-tree',base,env=env)
 for patch in patches:git('apply','--cached',str(patch),env=env)
 chain=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',chain).strip()
r={'base_commit':base,'previous_tree':before,'result_tree':chain,'patches':[str(p.relative_to(root)) for p in patches],'working_tree_matches_chain':True,'reverse_check':True,'whitespace_check':True}
(out/'patch-check-0035.json').write_text(json.dumps(r,indent=2)+'\n');print(chain)
