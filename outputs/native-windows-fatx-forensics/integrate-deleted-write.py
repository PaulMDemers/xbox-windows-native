"""Discard obsolete paging writes only for deleted, unopened, zero-allocation directories."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
base=json.loads((k/'patch-check-0080.json').read_text());current=json.loads((k/'patch-check-0082.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',current['result_tree']).strip()
# Both experimental changes are saved as patches and separately built artifacts.
# The production candidate branches from0080 and contains neither0081 nor0082.
for name in ['cleanup.c','rw.c']:
    rel='drivers/filesystems/vfatfs/'+name
    (repo/rel).write_bytes(git('show',base['result_tree']+':'+rel))
f=repo/'drivers/filesystems/vfatfs/rw.c';s=f.read_text()
mark='    /* A cached page can outlive a truncate. Paging writes never extend EOF:'
assert s.count(mark)==1
code='''    /* NT can submit dirty directory pages after the final delete cleanup.
     * No data remains to persist once this stream has no handles or backing
     * allocation. Discard those obsolete pages under PagingIoResource; never
     * follow the stale first-cluster field into possibly reused storage.
     * Keep normal range errors for live directories and volume/FAT streams. */
    if (PagingIo && !IsVolume && !IsFAT && vfatFCBIsDirectory(Fcb) &&
        BooleanFlagOn(Fcb->Flags, FCB_DELETE_PENDING) &&
        Fcb->OpenHandleCount == 0 &&
        Fcb->RFCB.FileSize.QuadPart == 0 &&
        Fcb->RFCB.AllocationSize.QuadPart == 0)
    {
        IrpContext->Irp->IoStatus.Information = 0;
        Status = STATUS_SUCCESS;
        goto ByeBye;
    }

'''
f.write_text(s.replace(mark,code+mark))
patch=k/'0083-vfat-deleted-directory-paging-write.patch';assert not patch.exists()
patch.write_bytes(git('diff',base['result_tree'],'--','drivers/filesystems/vfatfs/rw.c'))
with tempfile.TemporaryDirectory() as t:
    env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',base['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
    tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip();git('diff','--check',base['result_tree'])
r=dict(base,scope=__doc__,previous_tree=base['result_tree'],result_tree=tree,
       patches=base['patches']+[str(patch.relative_to(ws))],
       excluded_experiments=['0081','0082'],caveat='Requires unchanged rename regression, no new delayed-write events, and cold allocation/data validation. Physical corruption remains separate.')
(k/'patch-check-0083.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
