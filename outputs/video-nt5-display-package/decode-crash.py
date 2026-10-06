"""Decode kernel-only metadata from the retained post-bugcheck RAM; no guest access."""
import argparse,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;nt=k.parent/'native-windows-nt5-kernel'
p=argparse.ArgumentParser();p.add_argument('--case',choices=['004','005'],default='004');a=p.parse_args()
ram='reboot-crash.ram' if a.case=='004' else 'starttype-crash.ram'
data=(k/'artifacts'/ram).read_bytes();assert len(data)==64*1024**2
def phys32(a):return struct.unpack_from('<I',data,a)[0]
pubs=json.loads((nt/'kernel-publics.json').read_text())['symbols']
kernels=[]
for pos in range(0,len(data)-4096,4096):
    if data[pos:pos+2]!=b'MZ':continue
    off=phys32(pos+60)
    if off<4096 and data[pos+off:pos+off+4]==b'PE\0\0' and phys32(pos+off+8)==0x4b7a1bd5:kernels.append(pos)
def pa(va):
    pde=phys32(cr3+4*(va>>22));assert pde&1
    if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
    pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1
    return (pte&0xfffff000)+(va&4095)
def read(va,size):
    result=b''
    while size:
        at=pa(va);n=min(size,4096-(va&4095));assert at+n<=len(data)
        result+=data[at:at+n];va+=n;size-=n
    return result
def u32(a):return struct.unpack('<I',read(a,4))[0]
valid=[]
for cr3 in range(0,len(data)-4096,4096):
    entry=phys32(cr3+768*4)
    if not entry&1 or entry&0xfffff000!=cr3:continue
    for pos in kernels:
        base=0x80000000+pos
        try:
            if pa(base)==pos and u32(u32(base+pubs['_PsLoadedModuleList']['rva'])+24)==base:valid.append((cr3,base))
        except (AssertionError,struct.error):pass
assert valid and len({b for _,b in valid})==1
cr3,base=valid[0]
r=dict(scope=__doc__,ram_sha256=hashlib.sha256(data).hexdigest(),kernel_base=hex(base),
       kernel_mapping_candidates=[hex(c) for c,b in valid],selected_directory=hex(cr3),
       limits='Recovered self-referencing page directory, not captured CPU CR3; only shared kernel metadata is decoded.')
head=base+pubs['_PsLoadedModuleList']['rva'];link=u32(head);seen=set();modules=[]
while link!=head and link not in seen and len(seen)<256:
    seen.add(link);mb,entry,size=struct.unpack('<III',read(link+24,12));n,m,b=struct.unpack('<HHI',read(link+44,8));assert n<=m and n<1024
    modules.append(dict(name=read(b,n).decode('utf-16le') if n else '',base=hex(mb),entry=hex(entry),size=size));link=u32(link)
assert link==head;r['modules']=modules
r['bugcheck_data']=[hex(v) for v in struct.unpack('<5I',read(base+pubs['_KiBugCheckData']['rva'],20))]
fields=json.loads((nt/'pnp-layouts.json').read_text())['_DEVICE_NODE']['fields']
def field(n,f):return u32(n+fields[f]['offset'])
def uni(n,f):
    length,maximum,buffer=struct.unpack('<HHI',read(n+fields[f]['offset'],8));assert length<=maximum and length<=2048
    return read(buffer,length).decode('utf-16le') if length else ''
pending=[u32(base+pubs['_IopRootDeviceNode']['rva'])];seen=set();nodes=[]
while pending and len(seen)<256:
    n=pending.pop()
    if not n or n in seen:continue
    seen.add(n);nodes.append(dict(instance=uni(n,'InstancePath'),service=uni(n,'ServiceName'),problem=field(n,'Problem'),failure_status=hex(field(n,'FailureStatus'))))
    pending.extend([field(n,'Sibling'),field(n,'Child')])
r['pnp_tree']=nodes
(k/a.case/'crash.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(kernel=r['kernel_base'],bugcheck=r['bugcheck_data'],video_modules=[v for v in modules if any(t in v['name'].lower() for t in ['xwnfb','framebuf','xboxv','videoprt'])],gpu=[v for v in nodes if '02A0' in v['instance']]),indent=2))
