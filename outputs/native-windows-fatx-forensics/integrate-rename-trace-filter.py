"""Emulator-only rename lookup diagnostics; preserves all lookup and rename behavior."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
r=json.loads((k/'patch-check-0084.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',r['result_tree']).strip()
f=repo/'drivers/filesystems/vfatfs/finfo.c';s=f.read_text()
s=s.replace('XWN-RENAME-0084','XWN-RENAME-0085')
needle='    {\n        ULONG Index = ((ULONG)InterlockedIncrement(&XwnRenameTrace.Count) - 1) % 16;'
assert s.count(needle)==1
s=s.replace(needle,'    {\n        UNICODE_STRING Prefix = RTL_CONSTANT_STRING(L"\\\\xwnrotate");\n        UNICODE_STRING Parent = { 0 };\n        if (*ParentFCB) Parent = (*ParentFCB)->PathNameU;\n        if (Parent.Length >= Prefix.Length) Parent.Length = Prefix.Length;\n        if (RtlEqualUnicodeString(&Prefix, &Parent, TRUE))\n        {\n        ULONG Index = ((ULONG)InterlockedIncrement(&XwnRenameTrace.Count) - 1) % 16;')
needle='\n    /* If it exists */'
assert s.count(needle)==1;s=s.replace(needle,'\n    }\n'+needle)
f.write_text(s)
patch=k/'0085-vfat-rename-trace-filter.patch';assert not patch.exists();patch.write_bytes(git('diff',r['result_tree'],'--','drivers/filesystems/vfatfs/finfo.c'))
with tempfile.TemporaryDirectory() as t:
 env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',r['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
 tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip()
r.update(scope=__doc__,previous_tree=r['result_tree'],result_tree=tree,patches=r['patches']+[str(patch.relative_to(ws))],caveat='Diagnostic only, not for hardware deployment.')
(k/'patch-check-0085.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
