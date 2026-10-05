"""Replace only the filesystem driver in a disposable low/high allocation fixture."""
import argparse,hashlib,json,os,pathlib,struct,subprocess,sys,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();p.add_argument('--layout',choices=['low','high'],required=True);a=p.parse_args()
src=k/'artifacts/high-allocation-001.qcow2' if a.layout=='high' else ws/'outputs/native-windows-physical-f/artifacts/physical-cache-soak-001.qcow2'
target=k/('artifacts/rename-'+a.layout+'-001.qcow2');raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/rename-candidate.raw')
assert not raw.exists() and not target.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=dict(scope=__doc__,layout=a.layout,source_sha256=sha(src));patches=[]
data=(k/'artifacts/xwnfatx-rename-integration.sys').read_bytes()
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(src),str(raw)],check=True)
    with raw.open('rb') as f:
        fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
        path='winnt/system32/drivers/xwnfatx.sys';old=w.read(path)
        assert hashlib.sha256(old).hexdigest()=='f686b0a11395510176a60a23b90415f79c20e5a26dd4217130f27f32915b1884'
        parent=1
        for part in path.split('/')[:-1]:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part][2],44)[0]
        dc,off,e=w.directory(parent)['entries']['xwnfatx.sys'];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(data)<=len(chain)*65536
        for i,c in enumerate(chain):patches.append((w.p.cluster_offset(c),data[i*65536:(i+1)*65536].ljust(65536,b'\0')))
        entry=bytearray(w.read_cluster(dc));struct.pack_into('<I',entry,off+48,len(data));patches.append((w.p.cluster_offset(dc),entry))
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(src),str(target)],check=True)
    with tempfile.TemporaryDirectory(prefix='xwn-rename-driver-') as temp:
        cmd=[]
        for i,(at,b) in enumerate(patches):
            f=pathlib.Path(temp)/str(i);f.write_bytes(b);cmd+=['-c',f'write -q -s {f} {at} {len(b)}']
        subprocess.run(['qemu-io','-f','qcow2',*cmd,str(target)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',os.path.relpath(src,target.parent),str(target)],check=True)
    raw.unlink();subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
    with raw.open('rb') as f:assert Writer(f,fatx.open_partition(f,raw,'F')).read(path)==data
    assert sha(src)==r['source_sha256']
    r.update(driver_sha256=hashlib.sha256(data).hexdigest(),fixture_sha256=sha(target),readback_verified=True)
    (k/('rename-'+a.layout+'-fixture.json')).write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
