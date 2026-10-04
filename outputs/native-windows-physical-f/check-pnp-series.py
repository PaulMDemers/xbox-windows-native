import pathlib,json,subprocess,os,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f';s='/home/paul/xbox-windows-native/sources/reactos-extended';m=json.loads((k/'patch-check-0072.json').read_text())
fd,p=tempfile.mkstemp(prefix='xwn-index-');os.close(fd);os.unlink(p);env=dict(os.environ,GIT_INDEX_FILE=p)
def git(*args):return subprocess.check_output(['git','-C',s,*args],env=env).decode().strip()
try:
 git('read-tree',m['base_commit'])
 for patch in m['patches']:git('apply','--cached',str(ws/patch))
 tree=git('write-tree');assert tree==m['result_tree'];m['clean_index_replay_verified']=True;(k/'patch-check-0072.json').write_text(json.dumps(m,indent=2)+'\n');print(tree)
finally:os.unlink(p)
