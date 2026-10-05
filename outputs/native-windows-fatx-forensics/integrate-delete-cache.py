"""Experimental zero-truncate notification for a deleted directory's internal cache map."""
import json,os,pathlib,subprocess,tempfile
repo=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos-extended')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
previous=json.loads((k/'patch-check-0080.json').read_text());file=repo/'drivers/filesystems/vfatfs/cleanup.c'
def git(*args,env=None):return subprocess.check_output(['git',*args],cwd=repo,env=env)
assert not git('diff','--name-only',previous['result_tree']).strip()
old='''                PFILE_OBJECT tmpFileObject;
                tmpFileObject = pFcb->FileObject;'''
new='''                PFILE_OBJECT tmpFileObject;

                /* Deletion invalidates the stream, including an internal
                 * directory cache map. Tell NT's cache manager to purge it
                 * before releasing its backing clusters. A NULL truncate
                 * size can leave dirty directory pages pending for writeback. */
                pFcb->RFCB.ValidDataLength.QuadPart = 0;
                pFcb->RFCB.FileSize.QuadPart = 0;
                pFcb->RFCB.AllocationSize.QuadPart = 0;
                tmpFileObject = pFcb->FileObject;'''
text=file.read_text();assert text.count(old)==1;text=text.replace(old,new)
old='CcUninitializeCacheMap(tmpFileObject, NULL, NULL);';assert text.count(old)==1
text=text.replace(old,'CcUninitializeCacheMap(tmpFileObject, &pFcb->RFCB.FileSize, NULL);')
old='''
                pFcb->RFCB.ValidDataLength.QuadPart = 0;
                pFcb->RFCB.FileSize.QuadPart = 0;
                pFcb->RFCB.AllocationSize.QuadPart = 0;
            }''';assert text.count(old)==1;text=text.replace(old,'\n            }')
file.write_text(text)
patch=k/'0081-vfat-truncate-deleted-stream-cache.patch';assert not patch.exists()
patch.write_bytes(git('diff',previous['result_tree'],'--','drivers/filesystems/vfatfs/cleanup.c'))
with tempfile.TemporaryDirectory(prefix='xwn-delete-cache-') as temp:
    env=dict(os.environ,GIT_INDEX_FILE=temp+'/index');git('read-tree',previous['result_tree'],env=env)
    git('apply','--cached',str(patch),env=env);tree=git('write-tree',env=env).decode().strip()
    assert not git('diff','--name-only',tree).strip();git('diff','--check',previous['result_tree'])
r=dict(previous,scope=__doc__,previous_tree=previous['result_tree'],result_tree=tree,
       patches=previous['patches']+[str(patch.relative_to(ws))],
       caveat='Experimental; must eliminate the observed deleted-directory delayed-write warning without suppressing write errors.')
(k/'patch-check-0081.json').write_text(json.dumps(r,indent=2)+'\n');print(tree)
