"""Actual source resource validator, link-readiness method and codec-init fragment."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[1]);d=src/'drivers/wdm/audio/drivers/ac97'
out=k/'artifacts/codec-tests002';out.mkdir(parents=True,exist_ok=False)
common=(d/'common.cpp').read_text();adapter=(d/'adapter.cpp').read_text()
def function(s,start):
    a=s.index(start);b=s.index('{',a);depth=1;i=b+1
    while depth:
        depth+=(s[i]=='{')-(s[i]=='}');i+=1
    return s[a:i]
a=common.index('    // Identify before PC-only mixer/power probing.');b=common.index('\n#endif',a)
core=common[a:b]
prefix=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#define XBOX_NT5_AC97_MMIO 1
#define IN
#define PAGED_CODE() ((void)0)
#define DOUT(...) ((void)0)
#define READ_PORT_ULONG(p) readGlobalStatus()
using ULONG=uint32_t;using DWORD=uint32_t;using WORD=uint16_t;using USHORT=uint16_t;using UCHAR=uint8_t;
using NTSTATUS=int;using TopoNodeConfig=int;using TopoPinConfig=int;
const int STATUS_SUCCESS=0,STATUS_DEVICE_CONFIGURATION_ERROR=-1,STATUS_NOT_SUPPORTED=-2,STATUS_IO_DEVICE_ERROR=-3,STATUS_IO_TIMEOUT=-4;
const bool TRUE=true,FALSE=false;
#define NT_SUCCESS(x) ((x)>=0)
const int AC97REG_VENDOR_ID1=62,AC97REG_VENDOR_ID2=63,X_CR=11,X_SR=6,CR_RR=2,NODEC_TOP_ELEMENT=31,PINC_TOP_ELEMENT=17,PowerDeviceD0=1;
const int GLOB_CNT=0x2c,GLOB_STA_PCR=0x100,GLOB_CNT_COLD=2,GLOB_CNT_ACLOFF=8,GLOB_CNT_PRIE=16,KernelMode=0;
struct LARGE_INTEGER {int64_t QuadPart;};
static unsigned stalls,delays;
static void KeStallExecutionProcessor(unsigned n){stalls+=n;}
static void KeDelayExecutionThread(int,bool,LARGE_INTEGER* p){assert(p->QuadPart==-50000);++delays;}
static unsigned readGlobalStatus();
struct Physical {uint32_t LowPart=0;int32_t HighPart=0;};
struct Range {Physical Start;uint32_t Length=0;};
struct Descriptor {struct {Range Port,Memory;} u;};
using PCM_PARTIAL_RESOURCE_DESCRIPTOR=Descriptor*;
struct Resources {
 unsigned ports=0,memories=1,irqs=1,dmas=0;bool missingMemory=false,missingPort[2]={};Descriptor port[2],mem;
 Resources(){mem.u.Memory.Start.LowPart=0xfec00000;mem.u.Memory.Length=0x1000;port[0].u.Port.Start.LowPart=0xd000;port[0].u.Port.Length=0x100;port[1].u.Port.Start.LowPart=0xd200;port[1].u.Port.Length=0x80;}
 unsigned NumberOfPorts(){return ports;}unsigned NumberOfMemories(){return memories;}unsigned NumberOfInterrupts(){return irqs;}unsigned NumberOfDmas(){return dmas;}
 Descriptor* FindTranslatedPort(unsigned n){assert(n<2);return missingPort[n]?nullptr:&port[n];}
 Descriptor* FindTranslatedMemory(unsigned n){assert(n==0);return missingMemory?nullptr:&mem;}
};
using PRESOURCELIST=Resources*;
struct Write {unsigned address,value,width;};
struct CAC97AdapterCommon {
 bool m_FixedCodec207=false,m_FixedReady207=false,m_bDirectRead=true,allOnesGlobal=false,allOnesControl=false,allOnesHalt=false;
 unsigned id1=0x574d,id2=0x4c09,idReads=0,readError=0,globalControl=0,globalReadyAfter=0,globalReads=0,controlBusy=0,haltBusy=0,controlReads[2]={},haltReads[2]={},nodes=0,pins=0;
 int m_PowerState=0;std::vector<Write> writes;
 NTSTATUS PrimaryCodecReady();NTSTATUS Test207();
 unsigned ReadBMControlRegister32(unsigned p){assert(p==GLOB_CNT);return globalControl;}
 void WriteBMControlRegister(unsigned p,ULONG v){writes.push_back({p,v,4});}
 void WriteBMControlRegister(unsigned p,USHORT v){writes.push_back({p,v,2});}
 void WriteBMControlRegister(unsigned p,UCHAR v){writes.push_back({p,v,1});}
 UCHAR ReadBMControlRegister8(unsigned p){assert(p==0x1b||p==0x7b);unsigned e=p==0x7b;return allOnesControl?0xff:(controlReads[e]++<controlBusy?CR_RR:0);}
 USHORT ReadBMControlRegister16(unsigned p){assert(p==0x16||p==0x76);unsigned e=p==0x76;return allOnesHalt?0xffff:(haltReads[e]++<haltBusy?0:1);}
 NTSTATUS ReadCodecRegister(unsigned reg,WORD* result){assert(reg==AC97REG_VENDOR_ID1||reg==AC97REG_VENDOR_ID2);++idReads;if(idReads==readError)return STATUS_IO_DEVICE_ERROR;*result=reg==AC97REG_VENDOR_ID1?id1:id2;return 0;}
 void SetNodeConfig(int n,bool value){assert(!value&&n==(int)nodes);++nodes;}
 void SetPinConfig(int n,bool value){assert(!value&&n==(int)pins);++pins;}
};
static CAC97AdapterCommon* active;
static unsigned readGlobalStatus(){return active->allOnesGlobal?0xffffffff:(active->globalReads++>=active->globalReadyAfter?GLOB_STA_PCR:0);}
static int run(CAC97AdapterCommon& c){active=&c;stalls=delays=0;return c.Test207();}
'''
body=function(adapter,'NTSTATUS ValidateResources')+'\n'+function(common,'NTSTATUS CAC97AdapterCommon::PrimaryCodecReady')+'\nNTSTATUS CAC97AdapterCommon::Test207(){ NTSTATUS ntStatus;\n'+core+'\nreturn STATUS_SUCCESS;\n}\n'
tests=r'''
int main(){unsigned cases=0;
 for(unsigned p=0;p<4;p++)for(unsigned m=0;m<4;m++)for(unsigned i=0;i<4;i++)for(unsigned d=0;d<4;d++){
  Resources r;r.ports=p;r.memories=m;r.irqs=i;r.dmas=d;bool expected=(p==0||p==2)&&m==1&&i==1&&d==0;
  assert((ValidateResources(&r)==0)==expected);++cases;
 }
 for(unsigned n=0;n<2;n++){
  {Resources r;r.ports=2;r.missingPort[n]=true;assert(ValidateResources(&r)<0);++cases;}
  {Resources r;r.ports=2;r.port[n].u.Port.Start.HighPart=1;assert(ValidateResources(&r)<0);++cases;}
  for(unsigned length: {0u,0x7fu,0x10001u,0xffffffffu}){Resources r;r.ports=2;r.port[n].u.Port.Length=length;assert(ValidateResources(&r)<0);++cases;}
  {Resources r;r.ports=2;r.port[n].u.Port.Start.LowPart=0xffff;assert(ValidateResources(&r)<0);++cases;}
 }
 {Resources r;r.ports=2;r.port[1].u.Port.Start.LowPart=0xd080;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.ports=2;r.port[1].u.Port.Start.LowPart=0xd100;assert(ValidateResources(&r)==0);++cases;}
 {Resources r;r.missingMemory=true;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.mem.u.Memory.Start.HighPart=1;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.mem.u.Memory.Length=0x17f;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.mem.u.Memory.Start.LowPart=0xfec00001;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.mem.u.Memory.Start.LowPart=0xfffffffc;assert(ValidateResources(&r)<0);++cases;}
 {Resources r;r.mem.u.Memory.Start.LowPart=0xfffffe80;r.mem.u.Memory.Length=0x180;assert(ValidateResources(&r)==0);++cases;}
 {CAC97AdapterCommon c;assert(run(c)==0&&c.m_FixedCodec207&&c.m_FixedReady207&&!c.m_bDirectRead&&c.idReads==2&&c.nodes==31&&c.pins==17&&c.writes.size()==11);++cases;}
 {CAC97AdapterCommon c;c.id1=0x8384;c.id2=0x7600;assert(run(c)==0&&!c.m_FixedCodec207&&!c.m_FixedReady207&&c.writes.size()==1);++cases;}
 for(unsigned id: {0u,0xffffu,0x574cu,0x8385u}){CAC97AdapterCommon c;c.id1=id;assert(run(c)==STATUS_NOT_SUPPORTED&&!c.m_FixedReady207&&c.writes.size()==1);++cases;}
 {CAC97AdapterCommon c;c.id2=0xffff;assert(run(c)==STATUS_NOT_SUPPORTED);++cases;}
 for(unsigned error=1;error<=2;error++){CAC97AdapterCommon c;c.readError=error;assert(run(c)==STATUS_IO_DEVICE_ERROR&&!c.m_FixedReady207);++cases;}
 {CAC97AdapterCommon c;c.globalControl=0xffffffff;assert(run(c)==STATUS_IO_DEVICE_ERROR&&c.writes.empty()&&!c.idReads);++cases;}
 {CAC97AdapterCommon c;c.allOnesGlobal=true;assert(run(c)==STATUS_IO_TIMEOUT&&delays==201&&!c.idReads);++cases;}
 {CAC97AdapterCommon c;c.globalReadyAfter=201;assert(run(c)==STATUS_IO_TIMEOUT&&delays==201&&!c.idReads);++cases;}
 {CAC97AdapterCommon c;c.globalReadyAfter=200;assert(run(c)==0&&delays==200);++cases;}
 {CAC97AdapterCommon c;c.controlBusy=999;assert(run(c)==0&&stalls==1998);++cases;}
 {CAC97AdapterCommon c;c.controlBusy=1000;assert(run(c)==STATUS_IO_DEVICE_ERROR&&stalls==1000&&!c.m_FixedReady207&&c.writes.size()==3);++cases;}
 {CAC97AdapterCommon c;c.allOnesControl=true;assert(run(c)==STATUS_IO_DEVICE_ERROR&&stalls==1000&&!c.m_FixedReady207);++cases;}
 {CAC97AdapterCommon c;c.haltBusy=99;assert(run(c)==0&&stalls==198);++cases;}
 {CAC97AdapterCommon c;c.haltBusy=100;assert(run(c)==STATUS_IO_DEVICE_ERROR&&stalls==100&&!c.m_FixedReady207&&c.writes.size()==4);++cases;}
 {CAC97AdapterCommon c;c.allOnesHalt=true;assert(run(c)==STATUS_IO_DEVICE_ERROR&&stalls==100&&!c.m_FixedReady207&&c.writes.size()==4);++cases;}
 assert(cases==297);return 0;
}
'''
p=out/'actual-codec.cpp';p.write_text(prefix+body+tests)
subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined',str(p),'-o',str(out/'test')],check=True)
subprocess.run([str(out/'test')],check=True)
r=dict(passed=True,cases=297,scope=__doc__,common_sha256=hashlib.sha256(common.encode()).hexdigest(),adapter_sha256=hashlib.sha256(adapter.encode()).hexdigest(),test_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),asan=True,ubsan=True,physical_qualified=False)
(k/'codec-tests002.json').write_text(json.dumps(r,indent=2)+'\n');print('297 actual-source resource/codec/link cases passed')
