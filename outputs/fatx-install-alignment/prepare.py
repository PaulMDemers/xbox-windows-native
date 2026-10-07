"""Extend only SetupAPI log in a fresh owned pre-install child; preserve prefix and file identity."""
import importlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case in ['001','002']
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'fatx-first-install-0101/fixture-001.json').read_text())
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
control=(k.parent/'fatx-first-install-0101/001/artifacts/after-setupapi.log').read_bytes()
control_sha=m.sha(control);assert control_sha=='cd921b2c369d0978e3d56a6f75c7626b660e514b51c01cb80edb6674d274a4ef'
marker=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed'
control_offset=139166;desired_offset=270225
assert control[control_offset:].startswith(marker)
assert control[:control_offset].endswith(b'Copying file c:\\xwninf99\\xboxvnt5.sys to C:\\WINNT\\system32\\DRIVERS\\xboxvnt5.sys.\r\n')
pad_count=desired_offset-control_offset;assert pad_count==131059
# Comment-like ASCII lines only; deterministic exact byte count and CRLF ending.
line=b'; XWN ALIGNMENT FIXTURE PADDING ONLY '+b'.'*62+b'\r\n'
full,tail=divmod(pad_count,len(line))
assert tail>=3
padding=line*full+b';'+b'.'*(tail-3)+b'\r\n';assert len(padding)==pad_count
name='fatx-install-alignment-'+case
child=parent.with_name(name+'.qcow2');seed=ws/('work/'+name+'-seed.qcow2')
assert not child.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(child)],check=True)
m.target=child;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(child);w=m.Writer(io,m.fatx.open_partition(io,child,'F'))
path='winnt/setupapi.log';original=w.read(path);assert len(original)==135501 and control.startswith(original) and original.endswith(b'\r\n')
protected=[row['path'] for row in r['payloads']+r['preserved_payloads']]+['winnt/system32/drivers/xwnfatx.sys','winnt/system32/config/system','winnt/system32/config/software','winnt/system32/config/default','winnt/system32/config/sam','winnt/system32/config/security','winnt/system32/xwn-video-trace.bin']
preserved={p:m.sha(w.read(p)) for p in protected}
for row in r['payloads']+r['preserved_payloads']:assert preserved[row['path']]==row['sha256']
assert preserved['winnt/system32/drivers/xwnfatx.sys']==r['fatx_sha256']
for p,sha in r['preserved_during_observer_staging'].items():assert preserved[p]==sha
# Retain the existing directory slot, name, first cluster and original chain.
at=1;parts=w.parts(path)
for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
dc,off,entry=w.directory(at)['entries'][parts[-1].lower()]
first=struct.unpack_from('<I',entry,44)[0];old_chain=list(w.chain(first));old_fat=w.fat[:]
data=original+padding;cs=w.p.cluster_size
needed=(len(data)+cs-1)//cs;assert needed>len(old_chain)
added=w.allocate(needed-len(old_chain));assert all(old_fat[c]==0 for c in added)
w.fat[old_chain[-1]]=added[0];chain=old_chain+added
for i,c in enumerate(chain):w.write_cluster(c,data[i*cs:(i+1)*cs])
new_entry=bytearray(entry);struct.pack_into('<I',new_entry,48,len(data))
directory=bytearray(w.read_cluster(dc));directory[off:off+64]=new_entry;w.write_cluster(dc,directory)
assert bytes(new_entry[:48])==entry[:48] and bytes(new_entry[52:])==entry[52:]
assert [i for i,(a,b) in enumerate(zip(old_fat,w.fat)) if a!=b]==sorted([old_chain[-1]]+added)
w.flush();fresh=m.Writer(io,m.fatx.open_partition(io,child,'F'))
assert fresh.read(path)==data and list(fresh.chain(first))==chain
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
for p in ['xwnidle/result.log','xwnidle/windows.log']:
 try:fresh.read(p)
 except KeyError:pass
 else:raise AssertionError('Pre-install output exists: '+p)
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(child)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(child),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+child.name,str(seed)],check=True)
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,source_manifest='fatx-first-install-0101/fixture-001.json',fixture_name=child.name,fixture_sha256=m.filehash(child),seed_sha256=m.filehash(seed),preserved_during_alignment_staging=preserved,
 alignment=dict(control_sha256=control_sha,control_warning_offset=control_offset,target_offset=desired_offset,warning_index=1,padding_bytes=len(padding),padding_sha256=m.sha(padding),original_bytes=len(original),original_sha256=m.sha(original),before_bytes=len(data),before_sha256=m.sha(data),old_chain=old_chain,added_clusters=added,new_chain=chain,cluster_size=cs,directory_cluster=dc,directory_offset=off,original_entry_hex=entry.hex(),staged_entry_hex=bytes(new_entry).hex()),
 intervention='Only append deterministic ASCII padding to SetupAPI log, extending its existing chain. Unchanged prior helper, startup, hives, INF and drivers. Runtime warning alignment must be independently verified.',
 limits='UI-assisted diagnostic; path differs from physical xwninf102; padding extends allocation and changes log size. No root-cause, ordinary stability or hardware qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r['alignment'],indent=2))
