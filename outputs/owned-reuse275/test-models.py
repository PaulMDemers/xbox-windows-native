"""Fresh prelaunch negative controls; synthetic objects are explicitly modeled."""
import copy,hashlib,json,struct
from pathlib import Path
import objects,proof,terminal,oracle
from backend import validate_report
k=Path(__file__).resolve().parent;dest=k/'host001.json';assert not dest.exists()
checks=0;negatives=0
def okay(f):
    global checks
    f();checks+=1
def reject(f):
    global checks,negatives
    try:f()
    except (AssertionError,KeyError,ValueError,struct.error):checks+=1;negatives+=1;return
    raise AssertionError('Negative accepted')
pb=dict(_pb_FifoChannelID=0,_pb_GrCtxInst=4400,_pb_FreeInst=4400+0x3b5,
    _pb_DmaBuffer2=0x10000,_pb_DmaBuffer7=0x11000,_pb_DmaBuffer8=0x12000,_pb_DSAddr=0x400000,_pb_DepthStencilPitch=2560)
h=[0]*43;h[28:31]=[0x200000,2560,480]
ramht=bytearray(4096);memory={}
for handle in objects.CLASSES:
    graph=handle>=13;inst=(4400-11+objects.DMA_ORDER.index(handle)) if not graph else 4400+{13:0x37f,14:0x3b2,16:0x3b3,17:0x3b4}[handle]
    struct.pack_into('<II',ramht,handle*8,handle,0x80000000|(int(graph)<<16)|inst)
    if graph:w=[objects.CLASSES[handle]|(0x1000000 if handle==14 else 0),0,0,0]
    else:
        flags=0xb000|objects.CLASSES[handle];limit=0x3ffafff;base=0
        if handle in [2,7,8]:flags|=0x20000;base=pb['_pb_DmaBuffer'+str(handle)];limit=32 if handle==8 else 31
        if handle in [9,11]:base=h[28];limit=2560*480-1
        if handle==10:base=0x400000;limit=2560*480-1
        if handle==12:flags|=0x20000;limit=0x10000000
        w=[flags,limit,base|3,base|3]
    memory[0xfd700000+inst*16]=struct.pack('<4I',*w)+bytes((0x330-16) if handle==13 else 0)
def inspect(ht=ramht,mem=memory,p=pb):return objects.inspect(ht,p,h,lambda a,n,label:mem[a])
okay(inspect)
for handle in objects.CLASSES:
    z=bytearray(ramht);z[handle*8+6]^=1;reject(lambda:inspect(z))
    context=struct.unpack_from('<I',ramht,handle*8+4)[0];addr=0xfd700000+(context&65535)*16
    m=memory.copy();b=bytearray(m[addr]);b[0]^=1;m[addr]=bytes(b);reject(lambda:inspect(mem=m))
for name,value in [('_pb_FreeInst',0x3000),('_pb_FifoChannelID',1),('_pb_DSAddr',0x3fff000)]:
    p=pb.copy();p[name]=value;reject(lambda:inspect(p=p))
pack=struct.pack('<8I',0x401a8,12,0x81d8c,0xfd700100,42,0x40100,0xb2a,0)
# Exact packet extent excludes trailing zero, which is an invalid empty packet.
okay(lambda:objects.commands(pack[:-4]));reject(lambda:objects.commands(pack))
reject(lambda:objects.commands(struct.pack('<I',0x20000000)))
assert len(proof.vertices())==384
for u in range(4):
    expected=oracle.blocks()[u][256:768];rgba=bytes(v for i in range(0,512,4) for v in [expected[i+2],expected[i+1],expected[i],expected[i+3]])
    head=[terminal.MAGIC,273,0,u,10+u,100+u,30+u,2,5,20,0x20000+u*4096,512,0,0,16,8,0x8058,512,32,1,0,7,8,1]
    data=struct.pack('<24Q',*head)+bytes(32)+expected+rgba
    fn=lambda b:proof.snapshot(b,u,0,0x20000+u*4096,7,8)
    okay(lambda:fn(data))
    for pos in [0,8,16,24,80,88,104,112,120,128,136,144,152,160,168,176,184,224,735,736,1247]:
        b=bytearray(data);b[pos]^=1;reject(lambda:fn(bytes(b)))
    reject(lambda:fn(data[:-1]))
for epoch in [1,2]:
    n=dict(version=265,epoch=epoch,state=5,reason=0,overflow=0,accounting=0,shader_jobs_unknown=0,pending=0,reuse269_error=0,native_grant=0,retirement=0,cpu0_reason=0,cpu1_reason=0,cpu0_count=0,cpu1_count=0,cpu0_done=1,cpu1_done=1,render_fenced=1,display_fenced=1,worker=7,cpu0_thread=8,cpu1_thread=8,cpu0_epoch=epoch*2-1,cpu1_epoch=epoch*2,started=10,cpu0_when=11,cpu1_when=12,finished=13,deadline=14,pages=1,rows=1,sealed=epoch-1,context_match=epoch-1)
    fmt=lambda n:' '.join(f'{a}={b}' for a,b in n.items())
    okay(lambda:validate_report(fmt(n),epoch))
    for key in ['epoch','state','reason','overflow','accounting','shader_jobs_unknown','pending','reuse269_error','native_grant','retirement','cpu0_reason','cpu1_reason','cpu0_count','cpu1_count','cpu0_thread','cpu0_epoch','cpu1_epoch','sealed','context_match']:
        bad=n.copy();bad[key]+=1;reject(lambda:validate_report(fmt(bad),epoch))
    page=f'version=265 epoch={epoch} page=0 pages=1 rows=1 overflow=0 r0=3:0:1:0:0:0:0:0'
    okay(lambda:proof.pages([page],epoch,180000))
    reject(lambda:proof.pages([page],3-epoch,180000))
# Reuse the reviewed terminal's independent tests as frozen separate evidence;
# this kit adds header, identity and explicit epoch checks rather than requalifying old runs.
r=dict(passed=True,checks=checks,rejected_mutations=negatives,model_only=True,guest_launched=False,
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in k.glob('*.py')})
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:r[a] for a in ['passed','checks','rejected_mutations']},indent=2))
