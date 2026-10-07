"""Remove known namespace-to-file waits after the isolated cleanup correction."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
src=Path('/home/paul/xbox-windows-native/build/fatx-cleanup-order-001/source')
prior=ws/'outputs/fatx-cleanup-order';m=json.loads((prior/'manifest.json').read_text())
assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree']
subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
changes={}
def replace(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)

rel='drivers/filesystems/vfatfs/create.c';old=(src/rel).read_text();new=old
new=replace(new,'VfatCreateFile(\n    PDEVICE_OBJECT DeviceObject,\n    PIRP Irp)',
            'VfatCreateFile(\n    PDEVICE_OBJECT DeviceObject,\n    PIRP Irp,\n    PVFATFCB *WaitFcb)')
new=replace(new,'    BOOLEAN PagingFileCreate;\n','    BOOLEAN PagingFileCreate;\n    BOOLEAN OverwriteLocked = FALSE;\n')
marker='        if (PagingFileCreate)\n        {\n            /* FIXME:'
insert='''        /* Never wait for a file lock while holding the namespace lock.
         * On contention, retain the FCB only for a wait outside DirResource,
         * undo this incomplete open, and let the caller restart name/share
         * validation. No attributes, size or paging-file flags changed yet. */
        if (RequestedDisposition == FILE_OVERWRITE ||
            RequestedDisposition == FILE_OVERWRITE_IF ||
            RequestedDisposition == FILE_SUPERSEDE)
        {
            if (!ExAcquireResourceExclusiveLite(&pFcb->MainResource, FALSE))
            {
                vfatGrabFCB(DeviceExt, pFcb);
                *WaitFcb = pFcb;
                VfatCloseFile(DeviceExt, FileObject);
                return STATUS_PENDING;
            }
            OverwriteLocked = TRUE;
        }

'''
new=replace(new,marker,insert+marker)
# Three validation exits between the new acquisition and allocation unwind.
start=new.index(marker);end=new.index('            ExAcquireResourceExclusiveLite(&(pFcb->MainResource), TRUE);',start)
chunk=new[start:end];assert chunk.count('VfatCloseFile(DeviceExt, FileObject);')==3
lines=chunk.splitlines(True);fixed=[]
for line in lines:
    if 'VfatCloseFile(DeviceExt, FileObject);' in line:
        indent=line[:len(line)-len(line.lstrip())]
        fixed.append(indent+'if (OverwriteLocked) ExReleaseResourceLite(&pFcb->MainResource);\n')
    fixed.append(line)
new=new[:start]+''.join(fixed)+new[end:]
new=replace(new,'            ExAcquireResourceExclusiveLite(&(pFcb->MainResource), TRUE);',
            '            ASSERT(OverwriteLocked);')
new=replace(new,'            ExReleaseResourceLite(&(pFcb->MainResource));',
            '            ExReleaseResourceLite(&(pFcb->MainResource));\n            OverwriteLocked = FALSE;')
new=replace(new,'VfatCreate(\n    PVFAT_IRP_CONTEXT IrpContext)\n{\n    NTSTATUS Status;',
            'VfatCreate(\n    PVFAT_IRP_CONTEXT IrpContext)\n{\n    NTSTATUS Status;\n    PVFATFCB WaitFcb;')
new=replace(new,'''    ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
    Status = VfatCreateFile(IrpContext->DeviceObject, IrpContext->Irp);
    ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);''','''    for (;;)
    {
        WaitFcb = NULL;
        ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
        Status = VfatCreateFile(IrpContext->DeviceObject, IrpContext->Irp, &WaitFcb);
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
        if (!WaitFcb)
            break;

        ASSERT(Status == STATUS_PENDING);
        ExAcquireResourceExclusiveLite(&WaitFcb->MainResource, TRUE);
        ExReleaseResourceLite(&WaitFcb->MainResource);
        ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
        vfatReleaseFCB(IrpContext->DeviceExt, WaitFcb);
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
        /* The old pathname may have been renamed/deleted while unlocked.
         * Retry the full lookup and checks, never mutate the pinned old FCB. */
        IrpContext->Irp->IoStatus.Information = 0;
    }''')
changes[rel]=(old,new)

rel='drivers/filesystems/vfatfs/dir.c';old=(src/rel).read_text();new=old
before='''    if (!ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource,
                                        BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))'''
after='''    /* The open FILE_OBJECT pins pFcb; take its file lock before DirResource. */
    if (!ExAcquireResourceSharedLite(&pFcb->MainResource,
                                     BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))'''
new=replace(new,before,after)
new=replace(new,'''    if (!ExAcquireResourceSharedLite(&pFcb->MainResource,
                                     BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
    {
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);''','''    if (!ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource,
                                        BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
    {
        ExReleaseResourceLite(&pFcb->MainResource);''')
for indent in ['                ','            ','    ']:
    a=indent+'ExReleaseResourceLite(&pFcb->MainResource);\n'+indent+'ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);'
    b=indent+'ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);\n'+indent+'ExReleaseResourceLite(&pFcb->MainResource);'
    new=replace(new,a,b)
changes[rel]=(old,new)

rel='drivers/filesystems/vfatfs/finfo.c';old=(src/rel).read_text();new=old
start=new.index('    if (LockDir)\n    {\n        if (!ExAcquireResourceExclusiveLite(')
end=new.index('    switch (FileInformationClass)',start)
new=new[:start]+'''    /* Existing FILE_OBJECT ownership keeps FCB alive during both waits. */
    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
    {
        if (!ExAcquireResourceExclusiveLite(&FCB->MainResource,
                                            BooleanFlagOn(IrpContext->Flags, IRPCONTEXT_CANWAIT)))
        {
            return VfatMarkIrpContextForQueue(IrpContext);
        }
    }

    if (LockDir)
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
new=replace(new,'''    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
    {
        ExReleaseResourceLite(&FCB->MainResource);
    }

    if (LockDir)
    {
        ExReleaseResourceLite(&((PDEVICE_EXTENSION)IrpContext->DeviceObject->DeviceExtension)->DirResource);
    }''','''    if (LockDir)
    {
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
    }

    if (!BooleanFlagOn(FCB->Flags, FCB_IS_PAGE_FILE))
    {
        ExReleaseResourceLite(&FCB->MainResource);
    }''')
changes[rel]=(old,new)
patch=k/'0100-vfat-namespace-file-order.patch';assert not patch.exists()
patch.write_bytes(''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)) for rel,(a,b) in changes.items()).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Namespace/create lock-order candidate; requires runtime regressions and cold audit, not hardware qualified.')
m['patches'].append(str(patch.relative_to(ws)));(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text());l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest())
l['patch_sha256'][str(patch.relative_to(ws))]=hashlib.sha256(patch.read_bytes()).hexdigest();(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
(k/'build.py').write_text((prior/'build.py').read_text().replace('outputs/fatx-cleanup-order/inputs.json','outputs/fatx-namespace-order/inputs.json'))
print(tree)
