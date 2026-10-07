"""Cold-check raw C capture against exact virtual disk bytes and independent traversal."""
import importlib.util,io,json,pathlib,struct,subprocess,sys
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/raw-c-inventory';run=ws/'work/runs/raw-c-inventory-002'
spec=importlib.util.spec_from_file_location('ranges',ws/'outputs/native-windows-paint-save/prepare-fixture.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert (run/'cleanup.json').exists();disk=m.SliceIO(run/'hdd.qcow2');w=m.Writer(disk,m.fatx.open_partition(disk,run/'hdd.qcow2','E'))
out=k/'artifacts/emulator-002';out.mkdir(exist_ok=False)
for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:(out/name).write_bytes(w.read('Apps/XWNRawC/'+name))
assert w.read('Apps/XWNRawC/default.xbe')==(k/'artifacts/default.xbe').read_bytes()
lo=2359820288;length=524288000;disk.seek(lo);raw=disk.read(length);meta=(out/'fat-metadata.bin').read_bytes();assert raw[:len(meta)]==meta
m.fatx.PARTITIONS['CLOCAL']=(0,length);c=io.BytesIO(raw);w=m.Writer(c,m.fatx.open_partition(c,pathlib.Path('memory'),'CLOCAL'))
blob=(out/'directories.bin').read_bytes();actual=set();clusters=set()
for at in range(0,len(blob),80):
 typ,head,cluster,aux=struct.unpack_from('<4I',blob,at)
 if typ==1:assert w.fat[cluster]==aux;clusters.add(cluster)
 elif typ==2:assert w.read_cluster(cluster)[aux:aux+64]==blob[at+16:at+80];actual.add((head,cluster,aux))
 elif typ==5:assert at+80==len(blob)
 else:raise AssertionError(('Unexpected warning',typ))
expected=set();expected_clusters=set();queue=[1]
for head in queue:
 if not head:continue
 assert head not in expected_clusters;expected_clusters.update(w.chain(head))
 for _,(cluster,off,e) in w.directory(head)['entries'].items():
  expected.add((head,cluster,off))
  if e[1]&16:queue.append(struct.unpack_from('<I',e,44)[0])
assert expected==actual and expected_clusters==clusters
mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(run/'hdd.qcow2')]))
changed=[v for v in mapping if v.get('depth')==0 and v.get('data') and v['start']<lo+length and v['start']+v['length']>lo];assert not changed
subprocess.run([sys.executable,str(k/'analyze.py'),'--capture',str(out),'--output',str(k/'emulator-allocation.json')],check=True)
assert json.loads((k/'emulator-allocation.json').read_text())['allocation_consistent']
r=dict(scope=__doc__,passed=True,entries_verified=len(actual),directory_clusters_verified=len(clusters),exact_directory_coverage=True,no_C_overlay_writes=True,xbe_sha256=m.sha((k/'artifacts/default.xbe').read_bytes()))
(k/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
