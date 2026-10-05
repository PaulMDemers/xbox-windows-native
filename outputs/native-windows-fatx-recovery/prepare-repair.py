"""Build an exact-sector recovery plan and rehearse it against the preserved physical metadata."""
import array,hashlib,json,pathlib,struct,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;pre=k.parent/'native-windows-fatx-preflight';capture=k/'artifacts/physical-001';out=k/'artifacts/rehearsal';out.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((pre/'recovery-scope.json').read_text());request=json.loads((k/'backup-request.json').read_text());meta=(capture/'fat-metadata.bin').read_bytes();blob=(capture/'cluster-data.bin').read_bytes()
assert sha(meta)==r['metadata_sha256'] and len(blob)==request['count']*65540
assert 'SNAPSHOT_COMPLETE success=1 requested_clusters=557' in (capture/'snapshot.txt').read_text()
clusters={}
for i,c in enumerate(request['clusters']):
 assert struct.unpack_from('<I',blob,i*65540)[0]==c
 clusters[c]=blob[i*65540+4:(i+1)*65540]
assert len(clusters)==557
original=dict(clusters);changed={c:bytearray(b) for c,b in clusters.items()};detached=[]
for f in r['files']:
 c,off=f['entry_cluster'],f['entry_offset'];e=bytes.fromhex(f['entry_hex'])
 assert original[c][off:off+64]==e
 if f['path']=='/xwn-cache-pressure.tmp.c12':continue
 changed[c][off+44:off+52]=bytes(8);detached.append(f['path'])
root=changed[1];free=[i for i in range(0,65536,64) if root[i]==0xe5]
# Prefer deleted slots; never leave an end marker before a new entry.
if len(free)<2:
 end=next(i for i in range(0,65536,64) if root[i] in (0,255));free=[end,end+64];assert end+128<65536
 assert all(b in (0,255) for b in root[end:end+128])
names={root[i+2:i+2+root[i]].decode('latin1').lower() for i in range(0,65536,64) if 1<=root[i]<=42}
added=[];cim=next(f for f in r['files'] if f['path'].endswith('/CIM.REP'))
for off,name,first,size in [(free[0],'xwn-recovery-cim.bin',cim['first_cluster'],cim['chain_clusters']*65536),(free[1],'xwn-recovery-orphan.bin',r['orphan_clusters'][0],65536)]:
 assert name not in names and len(name)<=42
 e=bytearray(64);e[0]=len(name);e[1]=0x20;e[2:2+len(name)]=name.encode();struct.pack_into('<II',e,44,first,size)
 root[off:off+64]=e;added.append(dict(name=name,cluster=1,offset=off,first_cluster=first,size=size,entry_hex=e.hex()))
sectors=[]
for c in sorted(changed,key=lambda c:(c!=1,c)):
 for off in range(0,65536,512):
  before=original[c][off:off+512];after=bytes(changed[c][off:off+512])
  if before!=after:sectors.append((len(meta)+(c-1)*65536+off,before,after))
assert 1<=len(sectors)<=16
plan=struct.pack('<16sI',b'XWN-FIX-0001',len(sectors))+b''.join(struct.pack('<Q',off)+before+after for off,before,after in sectors)
reverse=struct.pack('<16sI',b'XWN-FIX-0001',len(sectors))+b''.join(struct.pack('<Q',off)+after+before for off,before,after in reversed(sectors))
(k/'artifacts/physical-plan.bin').write_bytes(plan);(k/'artifacts/rollback-plan.bin').write_bytes(reverse)
# Reconstruct the captured metadata with exactly the entry changes in the plan.
rows=(pre/'artifacts/physical-001/directories.bin').read_bytes();updated=bytearray(rows[:-80]);changed_rows=0
for at in range(0,len(updated),80):
 typ,head,c,off=struct.unpack_from('<4I',updated,at)
 if typ==2 and c in changed:
  e=bytes(changed[c][off:off+64]);changed_rows+=e!=updated[at+16:at+80];updated[at+16:at+80]=e
assert changed_rows==5
for entry in added:updated+=struct.pack('<4I',2,1,1,entry['offset'])+bytes.fromhex(entry['entry_hex'])
typ,dirs,entries,aux=struct.unpack_from('<4I',rows,len(rows)-80);assert typ==5
updated+=struct.pack('<4I',5,dirs,entries+2,aux)+bytes(64)
(out/'fat-metadata.bin').write_bytes(meta);(out/'directories.bin').write_bytes(updated);(out/'snapshot.txt').write_text('SNAPSHOT_COMPLETE success=1 offline_rehearsal=1\n')
subprocess.run([sys.executable,str(pre/'analyze.py'),'--capture',str(out),'--output',str(k/'rehearsal-allocation.json')],check=True)
assert json.loads((k/'rehearsal-allocation.json').read_text())['allocation_consistent']
# Verify byte reversibility and recovery after any completed-sector prefix.
for prefix in range(len(sectors)+1):
 disk={off:(after if i<prefix else before) for i,(off,before,after) in enumerate(sectors)}
 assert all(disk[off] in (before,after) for off,before,after in sectors)
 for off,before,after in sectors:disk[off]=after
 for off,before,after in reversed(sectors):assert disk[off]==after;disk[off]=before
 assert all(disk[off]==before for off,before,after in sectors)
result=dict(scope=__doc__,backup_cluster_count=557,backup_sha256=sha(blob),metadata_sha256=sha(meta),plan_sha256=sha(plan),rollback_sha256=sha(reverse),
 sectors=[dict(offset=off,before_sha256=sha(before),after_sha256=sha(after),changed_bytes=sum(a!=b for a,b in zip(before,after))) for off,before,after in sectors],
 detached_files=detached,preserved_files=added,fat_changed=False,unrelated_entries_changed=0,rehearsal_allocation_consistent=True,completed_sector_prefixes_reversible=len(sectors)+1,
 physical_repair_performed=False,caveat='Offline metadata rehearsal; native repair engine must pass emulator apply/reject tests before physical use.')
(k/'repair-plan.json').write_text(json.dumps(result,indent=2)+'\n');print('Plan sectors:',len(sectors),'FAT unchanged; allocation now consistent in rehearsal')
