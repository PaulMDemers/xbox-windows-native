"""Generate an isolated cleanup lock-order candidate from the exact0098 source."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
src=Path('/home/paul/xbox-windows-native/build/fatx-paging-eof-001/source')
prior=ws/'outputs/fatx-paging-eof';m=json.loads((prior/'manifest.json').read_text())
assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree']
subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
relative='drivers/filesystems/vfatfs/cleanup.c';old=(src/relative).read_text();new=old
def replace(before,after):
    global new
    assert new.count(before)==1,before
    new=new.replace(before,after)
replace('        ExAcquireResourceExclusiveLite(&pFcb->MainResource, TRUE);\n','        ASSERT(ExIsResourceAcquiredExclusive(&pFcb->MainResource));\n')
replace('        ExReleaseResourceLite(&pFcb->MainResource);\n','')
replace('    BOOLEAN Deleted;\n','    BOOLEAN Deleted;\n    PVFATFCB Fcb;\n    PERESOURCE MainResource = NULL;\n')
replace('    ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);\n    Deleted = VfatCleanupFile(IrpContext);\n    if (!Deleted) ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);',
'''    /* The open FILE_OBJECT retains this FCB through cleanup. Take its
     * MainResource before the namespace lock, just as file/volume flush does.
     * Waiting for MainResource while holding DirResource deadlocks a flush
     * that owns MainResource and is publishing the file's directory entry.
     * Volume cleanup does not take a per-file lock and may delete its VCB. */
    Fcb = IrpContext->FileObject->FsContext;
    if (Fcb && !BooleanFlagOn(Fcb->Flags, FCB_IS_VOLUME))
    {
        MainResource = &Fcb->MainResource;
        ExAcquireResourceExclusiveLite(MainResource, TRUE);
    }
    ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
    Deleted = VfatCleanupFile(IrpContext);
    if (!Deleted) ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
    if (MainResource) ExReleaseResourceLite(MainResource);''')
patch=k/'0099-vfat-cleanup-main-before-dir.patch';assert not patch.exists()
patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative)).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Cleanup-only causal candidate; other namespace/file lock inversions remain under investigation. No hardware qualification.')
m['patches'].append(str(patch.relative_to(ws)))
(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text());l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest())
l['patch_sha256'][str(patch.relative_to(ws))]=hashlib.sha256(patch.read_bytes()).hexdigest()
(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
build=(prior/'build.py').read_text().replace('outputs/fatx-paging-eof/inputs.json','outputs/fatx-cleanup-order/inputs.json')
(k/'build.py').write_text(build)
print(tree)
