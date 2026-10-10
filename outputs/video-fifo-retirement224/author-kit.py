"""Derive a bounded read-only preflight from the frozen222 CPU ownership bridge."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
old=k.parent/'video-resident-context222'
dest=k/'derivation.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((old/'build005.json').read_text())['source_pins']
for name in ['context.c','context.h','driver.c','probe.c']:
    assert sha(old/name)==pins[name]
    if name.startswith('context'):(k/name).write_bytes((old/name).read_bytes())
d=(old/'driver.c').read_text()
d=d.replace('device-policy changes, GPU MMIO, DMA descriptors or hardware writes.',
            'device-policy changes, DMA descriptors or hardware writes.224 adds bounded read-only GPU MMIO.')
d=d.replace('#include "context.h"','#include "context.h"\n#include "retirement.h"\n#ifndef X224_READS\n#define X224_READS 0\n#endif\n#define X224_IOCTL CTL_CODE(FILE_DEVICE_UNKNOWN,0x824,METHOD_BUFFERED,FILE_WRITE_ACCESS)')
needle='static const X222Ops Ops='
insert='''#if X224_READS
static unsigned char *FifoMap,*GraphMap;
static int gpu_read(void *unused,uint32_t index,uint32_t *value)
{
    uint32_t offset;(void)unused;
    if(index>=X224_WORDS || !FifoMap || !GraphMap)return 0;
    offset=X224Offsets[index];
    if(offset>=0x2000 && offset+4<=0x4000)
        *value=READ_REGISTER_ULONG((PULONG)(FifoMap+offset-0x2000));
    else if(offset>=0x400000 && offset+4<=0x401000)
        *value=READ_REGISTER_ULONG((PULONG)(GraphMap+offset-0x400000));
    else return 0;
    return 1;
}
static void free_maps(void)
{
    if(GraphMap){MmUnmapIoSpace(GraphMap,0x1000);GraphMap=NULL;}
    if(FifoMap){MmUnmapIoSpace(FifoMap,0x2000);FifoMap=NULL;}
}
#endif
static void retirement_query(PFILE_OBJECT owner,const X224Request *q,X224Reply *out)
{
    uint32_t i;uint32_t *p=(uint32_t *)out;
    for(i=0;i<sizeof(*out)/sizeof(*p);i++)p[i]=0;
    out->reasons=X224_NO_OWNERSHIP|X224_UNMODELED_BUSY;
    if(!passive(NULL)){out->status=X222_IRQL;return;}
    if(!enter(NULL)){out->status=X222_WAIT;return;}
    if(!Manager.memory || Manager.owner!=owner)out->status=X222_OWNER;
    else if(!q->generation || q->generation!=Manager.generation)out->status=X222_STALE;
    else {
#if X224_READS
        x224_sample(gpu_read,NULL,out);
#else
        out->status=X224_OFF;
#endif
    }
    leave(NULL);
}
'''
assert d.count(needle)==1;d=d.replace(needle,insert+needle)
needle='    irp->IoStatus.Status=status;irp->IoStatus.Information=bytes;'
insert='''    if(s->MajorFunction==IRP_MJ_DEVICE_CONTROL &&
       s->Parameters.DeviceIoControl.IoControlCode==X224_IOCTL) {
        status=STATUS_INVALID_PARAMETER;
        if(irp->AssociatedIrp.SystemBuffer &&
           s->Parameters.DeviceIoControl.InputBufferLength==sizeof(X224Request) &&
           s->Parameters.DeviceIoControl.OutputBufferLength>=sizeof(X224Reply)) {
            X224Request request=*(X224Request *)irp->AssociatedIrp.SystemBuffer;
            if(!request.reserved) {
                retirement_query(s->FileObject,&request,irp->AssociatedIrp.SystemBuffer);
                status=STATUS_SUCCESS;bytes=sizeof(X224Reply);
            }
        }
    }
'''
assert d.count(needle)==1;d=d.replace(needle,insert+needle)
d=d.replace('x222_initialize(&Manager);KeInitializeMutex(&Mutex,0);','''x222_initialize(&Manager);KeInitializeMutex(&Mutex,0);
#if X224_READS
    {
        PHYSICAL_ADDRESS a;
        a.QuadPart=0xfd002000;FifoMap=MmMapIoSpace(a,0x2000,MmNonCached);
        a.QuadPart=0xfd400000;GraphMap=MmMapIoSpace(a,0x1000,MmNonCached);
        if(!FifoMap || !GraphMap){free_maps();return STATUS_INSUFFICIENT_RESOURCES;}
    }
#endif''')
d=d.replace('if(!NT_SUCCESS(status))return status;','''if(!NT_SUCCESS(status)){
#if X224_READS
        free_maps();
#endif
        return status;
    }''')
d=d.replace('if(!NT_SUCCESS(status)){IoDeleteDevice(device);return status;}','''if(!NT_SUCCESS(status)){
        IoDeleteDevice(device);
#if X224_READS
        free_maps();
#endif
        return status;
    }''')
d=d.replace('XwnResident222','XwnResident224')
(k/'driver.c').write_text(d)
p=(old/'probe.c').read_text().replace('#include "context.h"','#include "context.h"\n#include "retirement.h"\n#define IOCTL224 CTL_CODE(FILE_DEVICE_UNKNOWN,0x824,METHOD_BUFFERED,FILE_WRITE_ACCESS)')
p=p.replace('XwnResident222','XwnResident224').replace('xwnctx222','xwnret224')
needle='    q=(X222Request){X222_INFO,0};'
insert='''    {
        X224Request q224={generation,0};X224Reply r224;DWORD n;
        HANDLE cpuLog=Log;
        Log=CreateFileA("C:\\\\xwnret224\\\\retirement.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
        if(Log==INVALID_HANDLE_VALUE)ExitProcess(92);
        if(!DeviceIoControl(other,IOCTL224,&q224,sizeof(q224),&r224,sizeof(r224),&n,NULL) || n!=sizeof(r224) || r224.status!=X222_OWNER || r224.reads)fail("RET_OWNER_FAIL");
        record("RET_OWNER",r224.status,r224.reads,r224.rounds);
        q224.generation=generation+1;
        if(!DeviceIoControl(owner,IOCTL224,&q224,sizeof(q224),&r224,sizeof(r224),&n,NULL) || r224.status!=X222_STALE || r224.reads)fail("RET_STALE_FAIL");
        record("RET_STALE",r224.status,r224.reads,r224.rounds);
        q224.generation=generation;
        if(DeviceIoControl(owner,IOCTL224,&q224,sizeof(q224)-1,&r224,sizeof(r224),&n,NULL))fail("RET_SHORT_ACCEPTED");
        if(!DeviceIoControl(owner,IOCTL224,&q224,sizeof(q224),&r224,sizeof(r224),&n,NULL) || n!=sizeof(r224))fail("RET_QUERY_FAIL");
        if(r224.status!=X224_OFF && r224.status!=X224_OBSERVED)fail("RET_STATUS_FAIL");
        if(r224.status==X224_OBSERVED && (r224.rounds!=8 || r224.reads!=128))fail("RET_COVERAGE_FAIL");
        if(r224.status==X224_OFF && (r224.rounds || r224.reads))fail("RET_OFF_READ_FAIL");
        if((r224.reasons&(X224_NO_OWNERSHIP|X224_UNMODELED_BUSY))!=(X224_NO_OWNERSHIP|X224_UNMODELED_BUSY))fail("RET_CAPABILITY_FAIL");
        record("RET_SUMMARY",r224.status,r224.rounds,r224.reads);
        record("RET_REASONS",r224.reasons,generation,0);
        for(DWORD round=0;round<r224.rounds;round++)for(DWORD j=0;j<X224_WORDS;j++)record("RET_WORD",round,j,r224.values[round][j]);
        record("RET_COMPLETE_NO_GRANT",224,0,0);CloseHandle(Log);Log=cpuLog;
    }
'''
assert p.count(needle)==1;p=p.replace(needle,insert+needle)
(k/'probe.c').write_text(p)
r=dict(parent_build_sha256=sha(old/'build005.json'),parents={n:pins[n] for n in ['context.c','context.h','driver.c','probe.c']},
       derived={n:sha(k/n) for n in ['context.c','context.h','driver.c','probe.c']},physical_access=False,gpu_writes=False,
       limits='222 CPU manager copied exactly; new guarded read-only request cannot grant GPU ownership or drain.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print('Native224 source derived; no build or launch')
