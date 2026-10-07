"""Preserve namespace-before-directory-stream order after the retained rename cycle."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
src=Path('/home/paul/xbox-windows-native/build/fatx-namespace-order-001/source')
prior=k.parent/'fatx-namespace-order';m=json.loads((prior/'manifest.json').read_text())
assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree']
subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
changes={}
def replace(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)

# Directory streams participate in namespace metadata flushes under DirResource.
# Restore query-directory's original ordering; ordinary files are different.
rel='drivers/filesystems/vfatfs/dir.c'
old=(src/rel).read_text()
new=Path('/home/paul/xbox-windows-native/build/fatx-cleanup-order-001/source',rel).read_text()
changes[rel]=(old,new)

rel='drivers/filesystems/vfatfs/cleanup.c';old=(src/rel).read_text();new=old
new=replace(new,'    BOOLEAN Deleted;','    BOOLEAN Deleted, Directory = FALSE;')
start=new.index('    /* The open FILE_OBJECT retains this FCB through cleanup.')
end=new.index('    IrpContext->Irp->IoStatus.Information = 0;',start)
new=new[:start]+'''    /* Ordinary files take MainResource before namespace metadata. Directory
     * streams are also flushed by rename while DirResource is held, so all
     * directory operations which need both locks take DirResource first.
     * The open FILE_OBJECT retains the FCB through cleanup. Volume cleanup
     * has no per-file lock and may delete its VCB. */
    Fcb = IrpContext->FileObject->FsContext;
    if (Fcb && !BooleanFlagOn(Fcb->Flags, FCB_IS_VOLUME))
    {
        MainResource = &Fcb->MainResource;
        Directory = vfatFCBIsDirectory(Fcb);
        if (!Directory)
            ExAcquireResourceExclusiveLite(MainResource, TRUE);
    }
    ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
    if (Directory)
        ExAcquireResourceExclusiveLite(MainResource, TRUE);
    Deleted = VfatCleanupFile(IrpContext);
    if (Directory)
        ExReleaseResourceLite(MainResource);
    if (!Deleted) ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
    if (MainResource && !Directory)
        ExReleaseResourceLite(MainResource);

'''+new[end:]
changes[rel]=(old,new)

rel='drivers/filesystems/vfatfs/finfo.c';old=(src/rel).read_text();new=old
new=replace(new,'    BOOLEAN LockDir;','    BOOLEAN LockDir, DirectoryLockFirst;')
start=new.index('    /* Existing FILE_OBJECT ownership keeps FCB alive during both waits. */')
end=new.index('    switch (FileInformationClass)',start)
new=new[:start]+'''    /* Parent directory cache flushes can occur inside rename. Keep directory
     * streams behind DirResource, while ordinary files retain Main-before-Dir.
     * The FILE_OBJECT pins this FCB across either acquisition order. */
    DirectoryLockFirst = LockDir && vfatFCBIsDirectory(FCB);
    if (DirectoryLockFirst &&
        !ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource,
                                        BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
        return VfatMarkIrpContextForQueue(IrpContext);

    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
    {
        if (!ExAcquireResourceExclusiveLite(&FCB->MainResource,
                                            BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
        {
            if (DirectoryLockFirst)
                ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
            return VfatMarkIrpContextForQueue(IrpContext);
        }
    }

    if (LockDir && !DirectoryLockFirst)
    {
        if (!ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource,
                                            BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
        {
            if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
                ExReleaseResourceLite(&FCB->MainResource);
            return VfatMarkIrpContextForQueue(IrpContext);
        }
    }

'''+new[end:]
new=replace(new,'''    if (LockDir)
    {
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
    }

    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
    {
        ExReleaseResourceLite(&FCB->MainResource);
    }''','''    if (LockDir && !DirectoryLockFirst)
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);

    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
        ExReleaseResourceLite(&FCB->MainResource);

    if (DirectoryLockFirst)
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);''')
changes[rel]=(old,new)

rel='drivers/filesystems/vfatfs/flush.c';old=(src/rel).read_text();new=old
new=replace(new,'''            ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
            Status = VfatFlushFile(DeviceExt, Fcb);
            ExReleaseResourceLite(&Fcb->MainResource);''','''            /* Rename flushes parent directory streams under DirResource.
             * A directory flush must not own MainResource while waiting for
             * that lock. Regular file flushes retain Main-before-Dir. */
            if (Pass)
                ExAcquireResourceExclusiveLite(&DeviceExt->DirResource, TRUE);
            ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
            Status = VfatFlushFile(DeviceExt, Fcb);
            ExReleaseResourceLite(&Fcb->MainResource);
            if (Pass)
                ExReleaseResourceLite(&DeviceExt->DirResource);''')
new=replace(new,'''        ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
        Status = VfatFlushFile(IrpContext->DeviceExt, Fcb);
        ExReleaseResourceLite (&Fcb->MainResource);''','''        if (vfatFCBIsDirectory(Fcb))
            ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
        ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
        Status = VfatFlushFile(IrpContext->DeviceExt, Fcb);
        ExReleaseResourceLite (&Fcb->MainResource);
        if (vfatFCBIsDirectory(Fcb))
            ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);''')
new=replace(new,''' * dropping it: ordinary file writes/flushes acquire MainResource first and
 * may then need DirResource. Waiting for MainResource with DirResource held
 * would deadlock those operations. Restore the caller's lock on every exit. */''',''' * dropping it: ordinary file writes/flushes acquire MainResource first and
 * may then need DirResource. Directory streams instead acquire DirResource
 * first because namespace changes flush their cache while holding it.
 * Restore the caller's lock on every exit. */''')
changes[rel]=(old,new)
patch=k/'0101-vfat-directory-stream-lock-order.patch';assert not patch.exists()
patch.write_bytes(''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)) for rel,(a,b) in changes.items()).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Separate regular-file and directory-stream lock orders; requires runtime regression and cold audits, not hardware qualified.')
m['patches'].append(str(patch.relative_to(ws)));(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text());l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest())
l['patch_sha256'][str(patch.relative_to(ws))]=hashlib.sha256(patch.read_bytes()).hexdigest();(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
(k/'build.py').write_text((prior/'build.py').read_text().replace('outputs/fatx-namespace-order/inputs.json','outputs/fatx-directory-order/inputs.json'))
print(tree)
