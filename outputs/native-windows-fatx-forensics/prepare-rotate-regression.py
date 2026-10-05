"""Stage synthetic rotation, unchanged rename regression and cache soak in an owned emulator overlay."""
import argparse,hashlib,json,pathlib,struct,subprocess,sys,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--diagnostic',action='store_true');g.add_argument('--filtered',action='store_true');g.add_argument('--unlinked',action='store_true');a=p.parse_args()
source=k/'artifacts/high-allocation-001.qcow2'
stem='rotate-trace' if a.diagnostic else 'rotate-regression'
if a.filtered:stem='rotate-filter'
if a.unlinked:stem='rotate-unlinked'
target=k/('artifacts/'+stem+'-001.qcow2')
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/rotate-regression.raw')
assert not raw.exists() and not target.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source_sha='18a72152df86ef61608836698758b0153ac365729518a89ed39ae93863d7d95c'
assert sha(source)==source_sha
rotate=(k/'artifacts/xwnrotate.exe').read_bytes()
probe=(ws/'outputs/native-windows-fatx-rename-boundary/artifacts/xwnfs.exe').read_bytes()
startup=b'@echo off\r\nC:\\xwnrename.exe\r\nif errorlevel 1 exit\r\nC:\\xwnrotate.exe\r\nif errorlevel 1 exit\r\nC:\\xwnphys2.exe\r\n'
patches=[]
class RecordedFile:
    def __init__(self,f):self.f=f
    def seek(self,*args):return self.f.seek(*args)
    def read(self,*args):return self.f.read(*args)
    def write(self,b):
        patches.append((self.f.tell(),bytes(b)))
        return self.f.write(b)
    def flush(self):self.f.flush()
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
    with raw.open('r+b') as f:
        fatx.PARTITIONS['F']=(15633072*512,472764096*512)
        w=Writer(RecordedFile(f),fatx.open_partition(f,raw,'F'))
        expected_driver='f686b0a11395510176a60a23b90415f79c20e5a26dd4217130f27f32915b1884'
        assert hashlib.sha256(w.read('winnt/system32/drivers/xwnfatx.sys')).hexdigest()==expected_driver
        name='xwnfatx-deleted-write.sys'
        expected='4aa035e6faa6b23ab7bfe78c6da10875eb8d789854c593983e0275c9141e2396'
        if a.diagnostic:
            name='xwnfatx-rename-trace.sys'
            expected='d3077970f9fc506b764e51ca8ed7364365c1c55f892cf4c981818b1b265c1921'
        if a.filtered:
            name='xwnfatx-rename-filter.sys'
            expected='1d170fc6ebd59889c8b819b3013dbf98373da7dcfb231f6e8843a1b19e7b6ba2'
        if a.unlinked:
            name='xwnfatx-unlinked.sys'
            expected='f74b55b7f81c7ee4a983d91022c9132c22c683538fb996e5c21f8c7a290734bd'
        driver=(k/'artifacts'/name).read_bytes()
        assert hashlib.sha256(driver).hexdigest()==expected
        parent=1
        for part in ['winnt','system32','drivers']:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part][2],44)[0]
        dc,off,e=w.directory(parent)['entries']['xwnfatx.sys'];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]))
        assert len(driver)<=len(chain)*w.p.cluster_size
        for i,c in enumerate(chain):w.write_cluster(c,driver[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
        entry=bytearray(w.read_cluster(dc));struct.pack_into('<I',entry,off+48,len(driver));w.write_cluster(dc,entry);w.dirs={}
        assert w.read('winnt/system32/drivers/xwnfatx.sys')==driver
        w.write('xwnrename.exe',probe)
        w.write('xwnrotate.exe',rotate)
        path='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
        assert w.read(path)==b'@echo off\r\nC:\\xwnphys2.exe\r\n'
        parent=1;parts=w.parts(path)
        for part in parts[:-1]:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part.lower()][2],44)[0]
        dc,off,e=w.directory(parent)['entries'][parts[-1].lower()]
        chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(startup)<=len(chain)*w.p.cluster_size
        for i,c in enumerate(chain):w.write_cluster(c,startup[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
        b=bytearray(w.read_cluster(dc));struct.pack_into('<I',b,off+48,len(startup));w.write_cluster(dc,b);w.dirs={};w.flush()
        assert w.read(path)==startup and w.read('xwnrename.exe')==probe and w.read('xwnrotate.exe')==rotate
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
    with tempfile.TemporaryDirectory(prefix='xwn-rename-regression-') as temp:
        commands=[]
        for i,(offset,data) in enumerate(patches):
            p=pathlib.Path(temp)/str(i);p.write_bytes(data);commands+=['-c',f'write -q -s {p} {offset} {len(data)}']
        subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
    raw.unlink();subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
    with raw.open('rb') as f:
        w=Writer(f,fatx.open_partition(f,raw,'F'));assert w.read(path)==startup and w.read('xwnrename.exe')==probe and w.read('xwnrotate.exe')==rotate
        assert w.read('winnt/system32/drivers/xwnfatx.sys')==driver
    assert sha(source)==source_sha
    r=dict(scope=__doc__,driver_artifact=name,driver_sha256=expected,source_sha256=source_sha,fixture_sha256=sha(target),probe_sha256=hashlib.sha256(probe).hexdigest(),rotate_sha256=hashlib.sha256(rotate).hexdigest(),readback_verified=True)
    (k/(stem+'-fixture.json')).write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
