"""New owned overlay: replace only the display DLL in the detached0096 fixture."""
import importlib,json,subprocess,sys,shutil,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-startup-detached-001.qcow2'
r=json.loads((ws/'outputs/video-startup-detached/fixture.json').read_text())
assert m.filehash(parent)==r['fixture_sha256']
assert json.loads((ws/'outputs/video-startup-detached/audit.json').read_text())['passed']
tests=json.loads((k/'compiled-tests.json').read_text());assert tests['passed']
m.target=parent.with_name('video-surface-lifecycle-002.qcow2');seed=ws/'work/video-surface-lifecycle-002-seed.qcow2'
assert not m.target.exists() and not seed.exists() and shutil.disk_usage('/mnt/c').free>8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(m.target);w=m.Writer(io,m.fatx.open_partition(io,m.target,'F'))
path='winnt/system32/framebuf.dll';before=w.read(path)
assert m.sha(before)==json.loads((k/'provenance.json').read_text())['files'][0]['sha256']
data=(k/'artifacts/framebuf.dll').read_bytes();assert m.sha(data)==tests['sha256']
# The new symbol-bearing display is larger than the baseline's allocation.
# Extend this one owned file only; preserve its existing chain and directory slot.
parts=w.parts(path);at=1
for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
dc,off,entry=w.directory(at)['entries'][parts[-1].lower()]
assert not entry[1]&16
oldchain=list(w.chain(struct.unpack_from('<I',entry,44)[0]));fat_before=list(w.fat)
needed=(len(data)+w.p.cluster_size-1)//w.p.cluster_size
added=w.allocate(max(0,needed-len(oldchain)))
if added:w.fat[oldchain[-1]]=added[0]
chain=oldchain+added
for i,c in enumerate(chain):w.write_cluster(c,data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
block=bytearray(w.read_cluster(dc));struct.pack_into('<I',block,off+48,len(data));w.write_cluster(dc,block);w.dirs={}
changed=[i for i,(a,b) in enumerate(zip(fat_before,w.fat)) if a!=b]
assert set(changed)==(set(added)|{oldchain[-1]} if added else set())
w.flush();assert w.read(path)==data
fresh=m.Writer(io,m.fatx.open_partition(io,m.target,'F'));assert fresh.read(path)==data
assert list(fresh.chain(oldchain[0]))==chain
r['display_allocation_growth']=dict(path=path,old_chain=oldchain,new_chain=chain,changed_fat_entries=changed,cluster_size=w.p.cluster_size,cold_readback_passed=True)
for row in r['payloads']:assert m.sha(w.read(row['path']))==row['sha256']
r['payloads'].append(dict(path=path,sha256=m.sha(data),bytes=len(data)))
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(m.target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(parent)==r['fixture_sha256']
r.update(scope=__doc__,parent_fixture_sha256=r['fixture_sha256'],fixture_sha256=m.filehash(m.target),seed_sha256=m.filehash(seed),baseline_display_sha256=m.sha(before),physical_access=False)
(k/'fixture.json').write_text(json.dumps(r,indent=2)+'\n');print('New display replacement overlay verified; no hardware access')
