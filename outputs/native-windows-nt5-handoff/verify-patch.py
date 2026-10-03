"""Verify complete patch chain with a disposable index in the private WSL clone."""
import json,os,pathlib,subprocess,tempfile
out=pathlib.Path(__file__).resolve().parent
root=out.parents[1];repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos')
base='afc0127e8f937ab68503d715d948844973756aa1';before='b6fb3f3be821ddb502a85f5c56d4af80177b4508'
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert git('rev-parse','HEAD').decode().strip()==base
patch=out/'0010-nt5-loader-extension-handoff.patch'
patch.write_bytes(git('diff','--binary',before,'--','boot/freeldr'))
patches=[root/p for p in json.loads((out.parent/'native-windows-nt5-debug/patch-check.json').read_text())['patches']]+[patch]
with tempfile.TemporaryDirectory(prefix='xwn-handoff-patch-') as tmp:
 env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index');git('read-tree',base,env=env)
 for p in patches:git('apply','--cached',str(p),env=env)
 expected=git('write-tree',env=env).decode().strip();git('add','-A',env=env)
 actual=git('write-tree',env=env).decode().strip();assert actual==expected
git('apply','--reverse','--check',str(patch));git('diff','--check')
report={'base_commit':base,'previous_tree':before,'result_tree':actual,'patches':[str(p.relative_to(root)) for p in patches],'complete_chain_matches_working_tree':True,'incremental_reverse_check':True,'whitespace_check':True}
(out/'patch-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
