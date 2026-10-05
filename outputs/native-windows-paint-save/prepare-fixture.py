"""Create a small emulator-only child of qualified r15, without a full raw disk copy."""
import hashlib,json,pathlib,shutil,struct,subprocess,sys,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-paint-save';source=ws/'work/runs/nt5-physical-f-high-allocation-r15/hdd.qcow2'
target=ws/'outputs/native-windows-fatx-forensics/artifacts/paint-save-001.qcow2';seed=ws/'work/paint-save-seed.qcow2'
checkpoint=target.parent/'paint-checkpoint-001.qcow2'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
sha=lambda b:hashlib.sha256(b).hexdigest()
def filehash(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

class SliceIO:
    """Sector-aligned reads/writes through qemu's raw range driver; child overlay only."""
    def __init__(self,path):self.path=path;self.pos=0
    def seek(self,offset,whence=0):
        assert whence==0 and offset>=0;self.pos=offset;return offset
    def read(self,n):
        assert n>0 and self.pos%512==0 and n%512==0
        with tempfile.TemporaryDirectory(prefix='xwn-paint-read-') as tmp:
            p=pathlib.Path(tmp)/'slice.bin'
            opts=f'driver=raw,offset={self.pos},size={n},file.driver=qcow2,file.file.filename={self.path}'
            subprocess.run(['qemu-img','dd','--image-opts','if='+opts,'of='+str(p),'bs=512','count='+str(n//512)],check=True,stdout=subprocess.DEVNULL)
            b=p.read_bytes();assert len(b)==n;self.pos+=n;return b
    def write(self,b):
        assert self.path==target and self.pos%512==0 and len(b)%512==0
        with tempfile.TemporaryDirectory(prefix='xwn-paint-write-') as tmp:
            p=pathlib.Path(tmp)/'slice.bin';p.write_bytes(b)
            subprocess.run(['qemu-io','-f','qcow2','-c',f'write -q -s {p} {self.pos} {len(b)}',str(self.path)],check=True,stdout=subprocess.DEVNULL)
        self.pos+=len(b);return len(b)
    def flush(self):pass # Each qemu-io process closes its child image.

def replace(w,path,data):
    at=1;parts=w.parts(path)
    for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
    dc,off,e=w.directory(at)['entries'][parts[-1].lower()];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(data)<=len(chain)*w.p.cluster_size
    for i,c in enumerate(chain):w.write_cluster(c,data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
    b=bytearray(w.read_cluster(dc));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(dc,b);w.dirs={}
    assert w.read(path)==data

if __name__=='__main__':
    assert not target.exists() and not seed.exists() and not checkpoint.exists()
    assert (source.parent/'cleanup.json').exists()
    assert json.loads((ws/'outputs/native-windows-fatx-forensics/nt5-physical-f-high-allocation-r15-qualification.json').read_text())['passed']
    before=filehash(source)
    shutil.copyfile(source,checkpoint)
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','lifetime-long-001.qcow2',str(checkpoint)],check=True)
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(checkpoint),str(target)],check=True)
    fatx.PARTITIONS['F']=(15633072*512,472764096*512)
    io=SliceIO(target);w=Writer(io,fatx.open_partition(io,target,'F'))
    filesystem=sha(w.read('winnt/system32/drivers/xwnfatx.sys'));assert filesystem=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'
    video=(ws/'outputs/native-windows-physical-f/artifacts/xboxvnt5-dimensions.sys').read_bytes()
    assert sha(video)=='f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb'
    old=sha(w.read('winnt/system32/drivers/xboxvnt5.sys'));assert old=='413098acf0066e48fde515b75d825578c23c17c4094ec2341ebdaa314a2d6b13'
    replace(w,'winnt/system32/drivers/xboxvnt5.sys',video)
    replace(w,'winnt/system32/xwn-video-trace.bin',b'XWN-VID-TRACE01\n'+bytes(4080))
    startup=b'@echo off\r\nstart C:\\WINNT\\system32\\mspaint.exe C:\\xwnpaint\\scribble.bmp\r\nexit\r\n'
    replace(w,'Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',startup)
    images=[]
    for item in json.loads((k/'images.json').read_text())['files']:
        data=(k/'artifacts/images'/item['name']).read_bytes();assert sha(data)==item['sha256'];images.append(w.write('xwnpaint/'+item['name'],data))
    w.flush()
    check=SliceIO(target);w=Writer(check,fatx.open_partition(check,target,'F'))
    for item in images:assert sha(w.read(item['path']))==item['sha256']
    assert sha(w.read('winnt/system32/drivers/xwnfatx.sys'))==filesystem
    assert w.read('winnt/system32/drivers/xboxvnt5.sys')==video
    assert filehash(source)==before
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',checkpoint.name,str(target)],check=True)
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/paint-save-001.qcow2',str(seed)],check=True)
    r=dict(scope=__doc__,source_run=source.parent.name,source_sha256=before,checkpoint_sha256=filehash(checkpoint),fixture_sha256=filehash(target),filesystem_sha256=filesystem,miniport_sha256=sha(video),startup_sha256=sha(startup),images=images,readback_verified=True,physical_access=False)
    r.update(fixture_name=target.name,trace_reset=True)
    (k/'fixture.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
