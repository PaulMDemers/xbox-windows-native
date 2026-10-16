"""Read-only source/fixture attestation, private linked symbols; no guest launch."""
import json,hashlib,subprocess,sys,os
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn412/preparation002')
assert not P.exists() and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P.parent)
P.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
xbe=Path('/mnt/e/xwn374/build001/default.xbe');assert sha(xbe)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
obj=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source/boot_xbe/xbeboot.o')
subprocess.run(['ld','-m','elf_i386','-Ttext','0x10000','-e','_start',str(obj),'-o',str(P/'original.elf')],check=True)
subprocess.run(['objcopy','-O','binary',str(P/'original.elf'),str(P/'original.bin')],check=True)
b=(P/'original.bin').read_bytes();a=xbe.read_bytes();assert b[0x1100:]==a[0x1100:0x3000] and len(b)==0x3000
symbols=subprocess.check_output(['nm','-n',str(P/'original.elf')],text=True);(P/'symbols.txt').write_text(symbols)
s={line.split()[2]:int(line.split()[0],16) for line in symbols.splitlines() if len(line.split())==3}
dis=subprocess.check_output(['objdump','-d','-Mintel',str(P/'original.elf')],text=True);(P/'disassembly.txt').write_text(dis)
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
f=json.loads((W/'outputs/install-validation406/assembly003.json').read_text());disk=Path(f['fixture_path_linux']);assert sha(disk)==f['fixture_sha256']
with ColdIO(disk) as io:
    rd=OemReader(io,m.fatx.open_partition(io,disk,'E'));installed=rd.read('Applications/XWNEBoot/default.xbe')
old_launcher_sha=hashlib.sha256(installed).hexdigest()
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
child=P/'fresh.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../../xwn406/assembly003/fresh.qcow2',str(child)],check=True)
with WriteIO(child,10000000000,P) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
    assert wr.read('Applications/XWNEBoot/default.xbe')==installed and len(installed)==len(a)
    import struct
    first=1
    for name in ['applications','xwneboot','default.xbe']:
        entry=wr.directory(first)['entries'][name][2]
        first=struct.unpack_from('<I',entry,44)[0]
    chain=list(wr.chain(first));assert len(chain)*wr.p.cluster_size>=len(a)
    for index,cluster in enumerate(chain):
        off=index*wr.p.cluster_size;piece=a[off:off+wr.p.cluster_size]
        if piece:
            data=bytearray(wr.read_cluster(cluster));data[:len(piece)]=piece;wr.write_cluster(cluster,data)
    change=dict(path='Applications/XWNEBoot/default.xbe',bytes=len(a),sha256=hashlib.sha256(a).hexdigest(),same_allocation_and_entry=True)
    wr.flush();io.flush()
with ColdIO(child) as io:
    rd=OemReader(io,m.fatx.open_partition(io,child,'E'));assert rd.read('Applications/XWNEBoot/default.xbe')==a
assert sha(disk)==f['fixture_sha256']
disk=child
result=dict(prepared=True,space=space,fixture=str(disk),fixture_sha256=sha(disk),never_executed_seed=True,old_launcher_sha256=old_launcher_sha,change=change,exact_original_launcher=True,original_xbe_sha256=sha(xbe),object_sha256=sha(obj),linked_code_exact_from_entry=True,symbols={n:s[n] for n in ['_start','blentry','newloc','ptr_newloc','bootloader_gdt','gdt_48_base','kernelram','phys_kernelram','bootloaderram','phys_bootloaderram','ptr_PAGE_SIZE']},physical_access=False,guest_launched=False,private_files={str(p):sha(p) for p in P.iterdir() if p.is_file()})
with (K/'preparation002.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
