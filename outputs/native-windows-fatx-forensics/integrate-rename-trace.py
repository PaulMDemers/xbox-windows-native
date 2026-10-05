"""Emulator-only rename lookup diagnostics; preserves all lookup and rename behavior."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
r=json.loads((k/'patch-check-0083.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',r['result_tree']).strip()
f=repo/'drivers/filesystems/vfatfs/finfo.c';s=f.read_text();mark='static NTSTATUS\nvfatPrepareTargetForRename('
trace='''/* Diagnostic-only RAM ring, no filesystem writes or status changes. */
struct {
    CHAR Signature[16];
    volatile LONG Count;
    struct { ULONG Words[8]; WCHAR Requested[128]; WCHAR Target[128]; } Entries[16];
} XwnRenameTrace = { "XWN-RENAME-0084", 0 };

'''
assert s.count(mark)==1;s=s.replace(mark,trace+mark)
start=s.index(mark);end=s.index('static\nBOOLEAN\nIsThereAChildOpened',start)
part=s[start:end].replace('PVFATFCB TargetFcb;','PVFATFCB TargetFcb = NULL;')
needle='    Status = vfatGetFCBForFile(DeviceExt, ParentFCB, &TargetFcb, NewName);'
assert part.count(needle)==1
part=part.replace(needle,needle+'''
    {
        ULONG Index = ((ULONG)InterlockedIncrement(&XwnRenameTrace.Count) - 1) % 16;
        RtlZeroMemory(&XwnRenameTrace.Entries[Index], sizeof(XwnRenameTrace.Entries[Index]));
        XwnRenameTrace.Entries[Index].Words[0] = Status;
        XwnRenameTrace.Entries[Index].Words[1] = ReplaceIfExists;
        XwnRenameTrace.Entries[Index].Words[2] = (ULONG)TargetFcb;
        XwnRenameTrace.Entries[Index].Words[6] = (ULONG)*ParentFCB;
        RtlCopyMemory(XwnRenameTrace.Entries[Index].Requested, NewName->Buffer,
                      min(NewName->Length, sizeof(XwnRenameTrace.Entries[Index].Requested) - sizeof(WCHAR)));
        if (NT_SUCCESS(Status) && TargetFcb)
        {
            XwnRenameTrace.Entries[Index].Words[3] = TargetFcb->Flags;
            XwnRenameTrace.Entries[Index].Words[4] = TargetFcb->dirIndex;
            XwnRenameTrace.Entries[Index].Words[5] = TargetFcb->startIndex;
            XwnRenameTrace.Entries[Index].Words[7] = vfatDirEntryGetFirstCluster(DeviceExt, &TargetFcb->entry);
            RtlCopyMemory(XwnRenameTrace.Entries[Index].Target, TargetFcb->PathNameU.Buffer,
                          min(TargetFcb->PathNameU.Length, sizeof(XwnRenameTrace.Entries[Index].Target) - sizeof(WCHAR)));
        }
    }
''')
f.write_text(s[:start]+part+s[end:])
patch=k/'0084-vfat-rename-lookup-trace.patch';assert not patch.exists();patch.write_bytes(git('diff',r['result_tree'],'--','drivers/filesystems/vfatfs/finfo.c'))
with tempfile.TemporaryDirectory() as t:
 env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',r['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
 tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip()
r.update(scope=__doc__,previous_tree=r['result_tree'],result_tree=tree,patches=r['patches']+[str(patch.relative_to(ws))],caveat='Diagnostic only, not for hardware deployment.')
(k/'patch-check-0084.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
