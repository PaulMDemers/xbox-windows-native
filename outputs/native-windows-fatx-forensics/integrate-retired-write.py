"""Serialize FATX unlink with paging I/O and discard writes only to fully retired file records."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
r=json.loads((k/'patch-check-0086.json').read_text());diagnostic=json.loads((k/'patch-check-0087.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',diagnostic['result_tree']).strip()
f=repo/'drivers/filesystems/vfatfs/rw.c';f.write_bytes(git('show',r['result_tree']+':drivers/filesystems/vfatfs/rw.c'));s=f.read_text()
needle='    /* NT can submit dirty directory pages after the final delete cleanup.'
assert s.count(needle)==1
s=s.replace(needle,'''    /* Replacement can retire a file while its cache still holds dirty pages.
     * FATXDelEntry takes this resource exclusively before unlink/free; once
     * retired, no paging write may follow its former chain into reused data.
     * Live files (including merely delete-pending open files) keep normal I/O. */
    if (PagingIo && !IsVolume && !IsFAT &&
        BooleanFlagOn(Fcb->Flags, FCB_NAMESPACE_UNLINKED) &&
        Fcb->OpenHandleCount == 0)
    {
        IrpContext->Irp->IoStatus.Information = Length;
        Status = STATUS_SUCCESS;
        goto ByeBye;
    }

'''+needle);f.write_text(s)
f=repo/'drivers/filesystems/vfatfs/dirwr.c';s=f.read_text();assert s.count('FATXDelEntry(')==1
s=s.replace('FATXDelEntry(','FATXDelEntryLocked(',1)
needle='/*\n * move an existing FAT entry\n */';assert s.count(needle)==1
s=s.replace(needle,'''/* Pair chain retirement with VfatWrite's shared paging acquisition. */
static NTSTATUS
FATXDelEntry(
    IN PDEVICE_EXTENSION DeviceExt,
    IN PVFATFCB pFcb,
    OUT PVFAT_MOVE_CONTEXT MoveContext)
{
    NTSTATUS Status;
    if (MoveContext != NULL)
        return FATXDelEntryLocked(DeviceExt, pFcb, MoveContext);

    ExAcquireResourceExclusiveLite(&pFcb->PagingIoResource, TRUE);
    Status = FATXDelEntryLocked(DeviceExt, pFcb, NULL);
    ExReleaseResourceLite(&pFcb->PagingIoResource);
    return Status;
}

'''+needle);f.write_text(s)
patch=k/'0088-vfat-retired-paging-write.patch';assert not patch.exists();patch.write_bytes(git('diff',r['result_tree'],'--','drivers/filesystems/vfatfs'))
with tempfile.TemporaryDirectory() as t:
 env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',r['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
 tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip();git('diff','--check',r['result_tree'])
r.update(scope=__doc__,previous_tree=r['result_tree'],result_tree=tree,patches=r['patches']+[str(patch.relative_to(ws))],excluded_experiments=r['excluded_experiments']+['0087'],caveat='Must pass unchanged dirty-replacement test and cold audit before physical use.')
(k/'patch-check-0088.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
