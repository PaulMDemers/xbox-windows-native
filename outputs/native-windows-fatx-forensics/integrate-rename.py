"""Integrate earlier experimental rename repairs with the validated 0079 source chain."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-fatx-forensics'
previous=json.loads((ws/'outputs/native-windows-physical-f/patch-check-0079.json').read_text())
extra=['0060-fatx-counted-rename-name.patch','0061-fatx-preserve-rename-indices.patch','0062-fatx-rename-logical-indices.patch']
patches=previous['patches']+['outputs/native-windows-fatx-rename-boundary/'+p for p in extra]
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',previous['result_tree']).strip(), 'Preserve unexpected source edits'
with tempfile.TemporaryDirectory(prefix='xwn-rename-integration-') as temp:
    env=dict(os.environ,GIT_INDEX_FILE=temp+'/index')
    git('read-tree',previous['base_commit'],env=env)
    for patch in patches:git('apply','--cached',str(ws/patch),env=env)
    tree=git('write-tree',env=env).decode().strip()
    changed=git('diff','--name-only',previous['result_tree'],tree).decode().splitlines()
    assert changed==['drivers/filesystems/vfatfs/dirwr.c'],changed
    for patch in patches[-3:]:git('apply',str(ws/patch))
    assert not git('diff','--name-only',tree).strip()
    git('diff','--check',previous['result_tree'])
r=dict(scope=__doc__,base_commit=previous['base_commit'],previous_tree=previous['result_tree'],result_tree=tree,
       patches=patches,clean_index_replay_verified=True,working_tree_matches_chain=True,
       caveat='0060-0062 were previously experimental due delayed writes; the combined candidate needs new runtime tests.')
(k/'patch-check-0080.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
