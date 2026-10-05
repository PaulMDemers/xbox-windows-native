"""Disposable emulator-only high FAT allocation/fragmentation experiment; no physical image."""
import hashlib, json, os, pathlib, shutil, struct, subprocess, sys, tempfile
ws = pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k = ws/'outputs/native-windows-fatx-forensics'
src = ws/'outputs/native-windows-physical-f/artifacts/physical-cache-soak-001.qcow2'
target = k/'artifacts/high-allocation-001.qcow2'
raw = pathlib.Path('/home/paul/xbox-windows-native/fixtures/high-allocation-001.raw')
sys.path[:0] = [str(ws/'outputs/native-windows-fatx-runtime'), '/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
assert not raw.exists() and not target.exists()
assert shutil.disk_usage(ws).free > 1250*1024*1024
sha = lambda b: hashlib.sha256(b).hexdigest()
def file_sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
r = dict(scope=__doc__, source_sha256=file_sha(src), first_high_cluster=2142521, relocations=[])
patches = {}
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(src),str(raw)],check=True)
    with raw.open('rb') as f:
        fatx.PARTITIONS['F'] = (15633072*512,472764096*512)
        w = Writer(f,fatx.open_partition(f,raw,'F'))
        cursor = r['first_high_cluster']
        for c in range(2,cursor):
            if w.fat[c] == 0: w.fat[c] = 0xfffffff7
        paths = ['winnt/system32/drivers/xwnfatx.sys','winnt/system32/wbem/repository/cim.rep',
                 'winnt/system32/wbem/repository/$winmgmt.cfg', 'winnt/system32/wbem/repository/$winmgmt.bak',
                 'xwn-cache-append.tmp','xwn-cache-map.tmp','xwn-cache-pressure.tmp']
        for path in paths:
            parent = 1; parts = w.parts(path)
            for name in parts[:-1]: parent = struct.unpack_from('<I',w.directory(parent)['entries'][name][2],44)[0]
            if parts[-1] not in w.directory(parent)['entries']:
                r['relocations'].append(dict(path=path,present=False));continue
            dc,off,e = w.directory(parent)['entries'][parts[-1]]
            old_first = struct.unpack_from('<I',e,44)[0]
            chain = list(w.chain(old_first)) if old_first else []
            data = w.read(path)
            new = list(range(cursor,cursor+max(1,len(chain))*3,3))
            assert all(w.fat[c] == 0 for c in range(cursor,new[-1]+3))
            for c in range(cursor,new[-1]+3): w.fat[c] = 0xfffffff7
            cursor = new[-1]+3
            for i,c in enumerate(new):
                w.fat[c] = new[i+1] if i+1<len(new) else 0xffffffff
                patches[w.p.cluster_offset(c)] = data[i*65536:(i+1)*65536].ljust(65536,b'\0')
            for c in chain: w.fat[c] = 0xfffffff7
            at = w.p.cluster_offset(dc)
            directory = bytearray(patches.get(at,w.read_cluster(dc)))
            struct.pack_into('<I',directory,off+44,new[0]);patches[at] = bytes(directory)
            r['relocations'].append(dict(path=path,present=True,old_first=old_first,new_chain=new,bytes=len(data),sha256=sha(data)))
        patches[w.p.fat_offset] = w.fat.tobytes()
        r['new_allocation_floor'] = cursor
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(src),str(target)],check=True)
    with tempfile.TemporaryDirectory(prefix='xwn-high-') as tmp:
        # Batch commands to avoid host command-line length limits.
        commands=[]
        for i,(at,data) in enumerate(patches.items()):
            p=pathlib.Path(tmp)/str(i);p.write_bytes(data)
            commands+=['-c',f'write -q -s {p} {at} {len(data)}']
            if len(commands)>=100:
                subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True,stdout=subprocess.DEVNULL);commands=[]
        if commands: subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',os.path.relpath(src,target.parent),str(target)],check=True)
    raw.unlink()
    subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
    with raw.open('rb') as f:
        w=Writer(f,fatx.open_partition(f,raw,'F'))
        for item in r['relocations']:
            if item['present']: assert sha(w.read(item['path']))==item['sha256']
        assert all(w.fat[c] for c in range(2,r['first_high_cluster']))
    assert file_sha(src)==r['source_sha256']
    r.update(fixture_sha256=file_sha(target), changed_bytes=sum(map(len,patches.values())), verified=True,
             caveat='Synthetic reserved low free space and fragmented high allocations; not an exact physical disk clone.')
    (k/'high-allocation-fixture.json').write_text(json.dumps(r,indent=2)+'\n')
    print({v:r[v] for v in ['fixture_sha256','changed_bytes','verified','new_allocation_floor']})
finally:
    raw.unlink(missing_ok=True)
