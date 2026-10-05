"""Emulator-only failure records; no error suppression or disk logging."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
r=json.loads((k/'patch-check-0086.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',r['result_tree']).strip()
f=repo/'drivers/filesystems/vfatfs/rw.c';s=f.read_text();mark='NTSTATUS\nVfatWrite(\n'
assert s.count(mark)==1
trace='''/* Bounded emulator diagnostic, read from RAM after the regression. */
typedef struct _XWN_WRITE_FAILURE {
    ULONG Words[16];
    WCHAR Name[64];
} XWN_WRITE_FAILURE;
struct {
    CHAR Signature[16];
    volatile LONG Count;
    XWN_WRITE_FAILURE Entries[16];
} XwnWriteFailureTrace = { "XWN-WRFAIL-0087", 0 };

static VOID XwnRecordWriteFailure(PVFAT_IRP_CONTEXT IrpContext, PVFATFCB Fcb, NTSTATUS Status)
{
    ULONG Index, Bytes;
    XWN_WRITE_FAILURE *Entry;
    if (NT_SUCCESS(Status) || !IrpContext->FileObject)
        return;
    Index = (ULONG)InterlockedIncrement(&XwnWriteFailureTrace.Count) - 1;
    Entry = &XwnWriteFailureTrace.Entries[Index % 16];
    RtlZeroMemory(Entry, sizeof(*Entry));
    Entry->Words[0] = Status;
    Entry->Words[1] = KeGetCurrentIrql();
    Entry->Words[2] = IrpContext->Irp->Flags;
    Entry->Words[10] = (ULONG)IrpContext->FileObject;
    if (!Fcb)
        return;
    Entry->Words[3] = Fcb->Flags;
    Entry->Words[4] = IrpContext->Stack->Parameters.Write.ByteOffset.LowPart;
    Entry->Words[5] = IrpContext->Stack->Parameters.Write.ByteOffset.HighPart;
    Entry->Words[6] = IrpContext->Stack->Parameters.Write.Length;
    Entry->Words[7] = Fcb->RFCB.FileSize.LowPart;
    Entry->Words[8] = Fcb->RFCB.AllocationSize.LowPart;
    Entry->Words[9] = vfatDirEntryGetFirstCluster(IrpContext->DeviceExt, &Fcb->entry);
    Entry->Words[10] = (ULONG)IrpContext->FileObject;
    Entry->Words[11] = Fcb->OpenHandleCount;
    Entry->Words[12] = Fcb->dirIndex;
    Entry->Words[13] = Fcb->startIndex;
    Entry->Words[14] = vfatFCBIsDirectory(Fcb);
    Entry->Words[15] = Fcb->RFCB.ValidDataLength.LowPart;
    Bytes = min(Fcb->PathNameU.Length, sizeof(Entry->Name) - sizeof(WCHAR));
    RtlCopyMemory(Entry->Name, Fcb->PathNameU.Buffer, Bytes);
}

'''
s=s.replace(mark,trace+mark)
start=s.index(mark);head=s[:start];body=s[start:]
assert body.count('    PVFATFCB Fcb;')==1;body=body.replace('    PVFATFCB Fcb;','    PVFATFCB Fcb = NULL;',1)
assert body.count('ByeBye:\n    if (Resource)')==1
body=body.replace('ByeBye:\n    if (Resource)','ByeBye:\n    XwnRecordWriteFailure(IrpContext, Fcb, Status);\n    if (Resource)',1)
f.write_text(head+body)
patch=k/'0087-vfat-write-failure-trace.patch';assert not patch.exists();patch.write_bytes(git('diff',r['result_tree'],'--','drivers/filesystems/vfatfs/rw.c'))
with tempfile.TemporaryDirectory() as t:
    env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',r['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
    tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip()
r.update(scope=__doc__,previous_tree=r['result_tree'],result_tree=tree,patches=r['patches']+[str(patch.relative_to(ws))],caveat='Diagnostic-only build on qualified0086; do not deploy to hardware.')
(k/'patch-check-0087.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
