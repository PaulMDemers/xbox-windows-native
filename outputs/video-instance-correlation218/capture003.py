"""Identify the actual loaded stock executable; no allocator or GPU operation."""
import json,sys,struct,time,hashlib,datetime,re
from pathlib import Path
from reader003 import Reader
k=Path(__file__).resolve().parent;ws=k.parents[1]
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs/stock-instance218-bootpath003')
dest=k/'bootpath003.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in json.loads((k/'emulator-frozen003.json').read_text()).items():assert sha(Path(path))==digest,path
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
r=dict(passed=False,debugger=True,ordinary_qualified=False,physical_access=False,host_allocator_invoked=False,gpu_writes=False,breakpoints=0,source_sha256=sha(Path(__file__)),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
g=None;lock=None;stopped=False
try:
    time.sleep(25);lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True
    g=Reader();r['features']=g.ask('qSupported');r['stop_reply']=g.ask('?');assert r['stop_reply'].startswith(('T','S'))
    base=0x80010000;h=g.read(base,4096);assert h[:2]==b'MZ'
    pe=struct.unpack_from('<I',h,0x3c)[0];assert h[pe:pe+4]==b'PE\0\0'
    size=struct.unpack_from('<I',h,pe+24+56)[0];assert 4096<=size<=4*1024*1024
    exp=struct.unpack_from('<I',h,pe+120)[0];assert exp+40<=size
    f=struct.unpack('<IIHHIIIIIII',g.read(base+exp,40));assert f[5]<=326<f[5]+f[6] and f[6]<=4096
    def ordinal(n):
        rv=struct.unpack('<I',g.read(base+f[8]+(n-f[5])*4,4))[0];assert 0<rv<size;return base+rv
    r['kernel_version']=struct.unpack('<HHHH',g.read(ordinal(324),8));assert r['kernel_version']==(1,0,4627,1)
    at=ordinal(326);length,maximum,buffer=struct.unpack('<HHI',g.read(at,8));assert 0<length<=512 and length<=maximum<=1024
    assert (0x80000000<=buffer and buffer+length<=0x84000000) or (0xd0000000<=buffer and buffer+length<=0xe0000000)
    r['registers']=command(4594,'info registers');cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',r['registers']).group(1),16);assert cr3&4095==0 and cr3<0x4000000
    def phys32(a):
        assert a%4==0 and 0<=a<=0x4000000-4
        raw=command(4594,f'xp /1wx 0x{a:x}');match=re.search(r'(?:0x)?[0-9a-fA-F]{8,16}:\s+0x([0-9a-fA-F]{8})',raw);assert match;return int(match.group(1),16)
    walks=[]
    for va in sorted(set([buffer&~4095,(buffer+length-1)&~4095])):
        pde=phys32(cr3+4*(va>>22));assert pde&1
        if pde&128:pa=(pde&0xffc00000)+(va&0x3fffff)
        else:
            pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1;pa=(pte&0xfffff000)+(va&4095)
        assert pa<0x4000000;walks.append(dict(virtual=va,physical=pa))
    r['name_ram_page_walks']=walks
    name=g.read(buffer,length);r['image_name_address']=at;r['image_name_length']=length;r['image_name_buffer']=buffer
    r['active_image_native_path']=name.decode('ascii');r['image_name_sha256']=hashlib.sha256(name).hexdigest()
    # Keep exact tentative app address read optional; a missing mapping cannot
    # change the kernel-owned executable-name observation into a failure.
    try:r['tentative_app_11000']=g.read(0x11000,64).hex()
    except Exception as exc:r['tentative_app_error']=repr(exc)
    r['passed']=True
except Exception as exc:r['error']=repr(exc);raise
finally:
    if g:g.s.close()
    if stopped:
        try:command(4594,'cont');r['resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
    if lock:lock.close()
    r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
    (run/'capture-complete.signal').write_text('boot path capture closed\n')
print(json.dumps({n:r.get(n) for n in ['passed','active_image_native_path','resumed']}))
