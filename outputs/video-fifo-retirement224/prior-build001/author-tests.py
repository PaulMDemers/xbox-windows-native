"""Host substitutes around the actual224 dispatch, including both read variants."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-resident-context222'
dest=k/'test-derivation.json';assert not dest.exists()
h=(old/'host-include/ddk/ntddk.h').read_text()
h=h.replace('#endif','''typedef ULONG *PULONG;
void *MmMapIoSpace(PHYSICAL_ADDRESS,ULONG,int);
void MmUnmapIoSpace(void *,ULONG);
ULONG READ_REGISTER_ULONG(PULONG);
#endif''')
p=k/'host-include/ddk/ntddk.h';p.parent.mkdir(parents=True);p.write_text(h)
t=(old/'test-bridge.c').read_text()
anchor='static IRP request(unsigned major,PFILE_OBJECT f)'
extra='''static ULONG FifoWords[0x2000/4],GraphWords[0x1000/4];
static unsigned GpuReads,MapCalls,MapFail=~0u,Maps;
void *MmMapIoSpace(PHYSICAL_ADDRESS a,ULONG n,int cache)
{
    assert(cache==MmNonCached);
    if(MapCalls++==MapFail)return NULL;
    Maps++;
    if(a.QuadPart==0xfd002000){assert(n==0x2000);FifoWords[(0x3214-0x2000)/4]=16;FifoWords[(0x2400-0x2000)/4]=16;return FifoWords;}
    assert(a.QuadPart==0xfd400000 && n==0x1000);return GraphWords;
}
void MmUnmapIoSpace(void *p,ULONG n)
{assert((p==FifoWords && n==0x2000)||(p==GraphWords && n==0x1000));assert(Maps);Maps--;}
ULONG READ_REGISTER_ULONG(PULONG p)
{
    unsigned i;
    for(i=0;i<X224_WORDS;i++) {
        uint32_t o=X224Offsets[i];PULONG expected=o<0x400000?FifoWords+(o-0x2000)/4:GraphWords+(o-0x400000)/4;
        if(p==expected){GpuReads++;return *p;}
    }
    assert(!"Read outside reviewed whitelist");return 0;
}
'''
assert t.count(anchor)==1;t=t.replace(anchor,extra+anchor)
anchor='int main(void)'
extra='''static X224Reply query(PDEVICE_OBJECT device,PFILE_OBJECT f,uint32_t generation,uint32_t reserved,ULONG length)
{
    X224Reply r={0};X224Request q={generation,reserved};IRP i=request(IRP_MJ_DEVICE_CONTROL,f);
    *(X224Request *)&r=q;i.AssociatedIrp.SystemBuffer=&r;
    i.stack.Parameters.DeviceIoControl.IoControlCode=X224_IOCTL;
    i.stack.Parameters.DeviceIoControl.InputBufferLength=length;
    i.stack.Parameters.DeviceIoControl.OutputBufferLength=sizeof(r);
    NTSTATUS s=dispatch(device,&i);
    assert(i.completed && !Locked);
    if(reserved || length!=sizeof(q))assert(s==STATUS_INVALID_PARAMETER && !i.IoStatus.Information);
    else assert(s==STATUS_SUCCESS && i.IoStatus.Information==sizeof(r));
    return r;
}
'''
t=t.replace(anchor,extra+anchor)
anchor='    assert(DriverEntry(&d,&u)==STATUS_SUCCESS && !d.DriverUnload);'
extra='''#if X224_READS
    MapFail=0;assert(DriverEntry(&d,&u)==STATUS_INSUFFICIENT_RESOURCES && !Maps);
    MapCalls=0;MapFail=1;assert(DriverEntry(&d,&u)==STATUS_INSUFFICIENT_RESOURCES && !Maps);
    MapCalls=0;MapFail=~0u;
#endif
'''
t=t.replace(anchor,extra+anchor)
anchor='    IRP clean=request(IRP_MJ_CLEANUP,&owner);'
extra='''    X224Reply r224=query(&device,&other,reply.generation,0,sizeof(X224Request));
    assert(r224.status==X222_OWNER && !GpuReads && !r224.reads);
    r224=query(&device,&owner,reply.generation+1,0,sizeof(X224Request));assert(r224.status==X222_STALE && !GpuReads);
    query(&device,&owner,reply.generation,1,sizeof(X224Request));query(&device,&owner,reply.generation,0,7);assert(!GpuReads);
    Elevated=1;r224=query(&device,&owner,reply.generation,0,sizeof(X224Request));Elevated=0;assert(r224.status==X222_IRQL && !GpuReads);
    FailWait=1;r224=query(&device,&owner,reply.generation,0,sizeof(X224Request));assert(r224.status==X222_WAIT && !GpuReads);
    r224=query(&device,&owner,reply.generation,0,sizeof(X224Request));
#if X224_READS
    assert(r224.status==X224_OBSERVED && GpuReads==128 && r224.reads==128 && r224.rounds==8);
#else
    assert(r224.status==X224_OFF && !GpuReads && !r224.reads && !r224.rounds);
#endif
    assert(r224.reasons==(X224_NO_OWNERSHIP|X224_UNMODELED_BUSY));
'''
assert t.count(anchor)==1;t=t.replace(anchor,extra+anchor)
t=t.replace('    return 0;\n}', '''#if X224_READS
    free_maps();assert(!Maps);
#endif
    return 0;
}''')
(k/'test-bridge.c').write_text(t)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(parent_header_sha256=sha(old/'host-include/ddk/ntddk.h'),parent_test_sha256=sha(old/'test-bridge.c'),derived_header_sha256=sha(p),derived_test_sha256=sha(k/'test-bridge.c')),indent=2)+'\n')
