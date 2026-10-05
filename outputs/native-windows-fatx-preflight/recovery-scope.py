"""Derive a bounded recovery scope from the preserved full-F snapshot; never edits a disk."""
import array,collections,hashlib,json,pathlib,struct
k=pathlib.Path(__file__).resolve().parent;capture=k/'artifacts/physical-001'
audit=json.loads((k/'physical-allocation.json').read_text());assert audit['capture_complete']
meta=(capture/'fat-metadata.bin').read_bytes();rows=(capture/'directories.bin').read_bytes()
assert hashlib.sha256(meta).hexdigest()==audit['metadata_sha256']
assert hashlib.sha256(rows).hexdigest()==audit['directory_records_sha256']
fat=array.array('I');fat.frombytes(meta[4096:]);limit=(472764096*512-len(meta))//65536+1
entries=collections.defaultdict(list)
for at in range(0,len(rows),80):
 typ,head,c,offset=struct.unpack_from('<4I',rows,at)
 if typ==2:entries[head].append((c,offset,rows[at+16:at+80]))
affected={e['path'] for e in audit['errors']}|{e['other'] for e in audit['errors'] if 'other' in e}
objects={};queue=[(1,'')];seen=set()
for head,parent in queue:
 if not head:continue
 assert head not in seen;seen.add(head)
 for c,off,e in entries[head]:
  assert 1<=e[0]<=42
  name=e[2:2+e[0]].decode('latin1');path=parent+'/'+name;first,size=struct.unpack_from('<II',e,44)
  if e[1]&16:queue.append((first,path));continue
  if path not in affected:continue
  chain=[];s=set();cur=first
  while 0<cur<limit and cur not in s:
   s.add(cur);chain.append(cur);cur=fat[cur]
  objects[path]=dict(path=path,entry_cluster=c,entry_offset=off,entry_hex=e.hex(),first_cluster=first,size=size,
    required_clusters=(size+65535)//65536,chain_clusters=len(chain),terminal=f'{cur:08x}',chain=chain)
assert set(objects)==affected
shared=collections.defaultdict(list)
for path,item in objects.items():
 for c in item['chain']:shared[c].append(path)
shared={c:paths for c,paths in shared.items() if len(paths)>1}
for path,item in objects.items():
 item['shared_clusters']=sum(c in shared for c in item['chain'])
 item['shared_within_logical_file']=sum(c in shared for c in item['chain'][:item['required_clusters']])
old=json.loads((k.parent/'native-windows-fatx-forensics/physical-snapshot.json').read_text())
oldfat=next(f for f in old['files'] if f['name']=='fat-metadata.bin')['sha256']
assert oldfat==audit['metadata_sha256'],'Allocation changed since preserved cycle013 snapshot'
known=lambda p:p.startswith('/winnt/') or p.startswith('/documents and settings/') or p=='/xwn-cache-pressure.tmp.c12'
assert all(known(p) for p in affected),'Review unexpected non-Windows damage separately'
summary=dict(scope=__doc__,metadata_sha256=audit['metadata_sha256'],fat_matches_prior_physical013=True,
 unique_affected_files=len(objects),error_records=len(audit['errors']),unique_shared_clusters=len(shared),
 all_reported_conflicts_within_owned_windows_or_test_files=True,
 orphan_clusters=audit['orphan_cluster_sample'],files=list(objects.values()),
 windows_boot_ready=False,physical_F_changes_performed=False,
 next_steps=['Preserve affected raw clusters and directory entries, including orphan storage.',
 'Rehearse detaching corrupt entries without freeing clusters still owned by another entry.',
 'Restore affected Windows files from verified sources, retaining the physical HAL and trace miniport.',
 'Re-scan allocation and audit Windows binaries/hives before enabling a bounded driver trial.'],
 caveat='No allocation conflicts observed outside owned Windows/test files; unrelated payload contents were not verified. Do not delete crosslinked files through normal FTP deletion.')
(k/'recovery-scope.json').write_text(json.dumps(summary,indent=2)+'\n')
print({key:summary[key] for key in ['unique_affected_files','error_records','unique_shared_clusters','fat_matches_prior_physical013']})
for v in objects.values():print(v['path'], {key:v[key] for key in ['size','required_clusters','chain_clusters','shared_clusters','shared_within_logical_file','terminal']})
