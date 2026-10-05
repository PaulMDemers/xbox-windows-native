"""Keep unlinked FATX FCBs alive for cache references without reusing their old namespace entries."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
base=json.loads((k/'patch-check-0083.json').read_text());current=json.loads((k/'patch-check-0085.json').read_text())
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',current['result_tree']).strip()
rel='drivers/filesystems/vfatfs/finfo.c';(repo/rel).write_bytes(git('show',base['result_tree']+':'+rel))
f=repo/'drivers/filesystems/vfatfs/vfat.h';s=f.read_text();needle='#define FCB_DELAYED_CLOSE       0x0040'
assert s.count(needle)==1;s=s.replace(needle,needle+'\n/* The FATX directory entry is gone; references may still await cache close. */\n#define FCB_NAMESPACE_UNLINKED  0x0200');f.write_text(s)
f=repo/'drivers/filesystems/vfatfs/fcb.c';s=f.read_text();needle='            rcFCB = entry->self;'
assert s.count(needle)==1;s=s.replace(needle,needle+'''
            /* A delayed cache close must not make a deleted name exist again.
             * Keep the FCB hashed until its final release, but skip name lookup. */
            if (BooleanFlagOn(rcFCB->Flags, FCB_NAMESPACE_UNLINKED))
            {
                entry = entry->next;
                continue;
            }
''');f.write_text(s)
f=repo/'drivers/filesystems/vfatfs/dirwr.c';s=f.read_text();start=s.index('VfatUpdateEntry(');end=s.index('vfatRenameEntry(',start);part=s[start:end]
needle='    ASSERT(pFcb);';assert part.count(needle)==1
part=part.replace(needle,needle+'''

    if (BooleanFlagOn(pFcb->Flags, FCB_NAMESPACE_UNLINKED))
    {
        ClearFlag(pFcb->Flags, FCB_IS_DIRTY);
        return STATUS_SUCCESS;
    }
''');s=s[:start]+part+s[end:]
start=s.index('FATXDelEntry(');end=s.index('VfatMoveEntry(',start);part=s[start:end]
needle='    StartIndex = pFcb->startIndex;';assert part.count(needle)==1
part=part.replace(needle,'''    /* A second delete must not free storage already reused by another file. */
    if (BooleanFlagOn(pFcb->Flags, FCB_NAMESPACE_UNLINKED))
        return MoveContext == NULL ? STATUS_SUCCESS : STATUS_FILE_DELETED;

'''+needle)
needle="    if (MoveContext == NULL)\n    {";assert part.count(needle)==1
part=part.replace(needle,needle+'''
        /* Only a true unlink retires this name; a move retains the live FCB. */
        SetFlag(pFcb->Flags, FCB_NAMESPACE_UNLINKED);
        ClearFlag(pFcb->Flags, FCB_IS_DIRTY);
''');f.write_text(s[:start]+part+s[end:])
patch=k/'0086-vfat-unlinked-fcb-namespace.patch';assert not patch.exists();patch.write_bytes(git('diff',base['result_tree'],'--','drivers/filesystems/vfatfs'))
with tempfile.TemporaryDirectory() as t:
 env=dict(os.environ,GIT_INDEX_FILE=t+'/index');git('read-tree',base['result_tree'],env=env);git('apply','--cached',str(patch),env=env)
 tree=git('write-tree',env=env).decode().strip();assert not git('diff','--name-only',tree).strip();git('diff','--check',base['result_tree'])
r=dict(base,scope=__doc__,previous_tree=base['result_tree'],result_tree=tree,patches=base['patches']+[str(patch.relative_to(ws))],excluded_experiments=['0081','0082','0084','0085'],caveat='Requires repeat rotation/reuse and cold validation; physical corruption linkage unproven.')
(k/'patch-check-0086.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
