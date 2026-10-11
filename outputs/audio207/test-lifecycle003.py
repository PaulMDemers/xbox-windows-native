"""Compile actual changed methods with adversarial MMIO/interrupt test doubles."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[1]);d=src/'drivers/wdm/audio/drivers/ac97';out=k/'artifacts/tests003';out.mkdir(parents=True,exist_ok=False)
s=(d/'stream.cpp').read_text()
def function(start):
    a=s.index(start);b=s.index('{',a);depth=1;i=b+1
    while depth:
        depth+=(s[i]=='{')-(s[i]=='}');i+=1
    return s[a:i]
body=function('int CMiniportStream::GetBuffPos')+'\n'+function('NTSTATUS NTAPI CMiniportStream::Quiesce207(PINTERRUPTSYNC')
prefix=r'''
#include <cassert>
#include <cstdint>
#include <cstddef>
#include <vector>
#define XBOX_NT5_AC97_MMIO 1
#define NTAPI
#define UNREFERENCED_PARAMETER(x) (void)(x)
using UCHAR=uint8_t;using USHORT=uint16_t;using DWORD=uint32_t;using ULONG=uint32_t;
using NTSTATUS=int;using PVOID=void*;using PINTERRUPTSYNC=void*;
const int STATUS_SUCCESS=0,STATUS_IO_DEVICE_ERROR=-1;
const bool TRUE=true;
const int X_CR=11,X_CIV=4,X_PICB=8,X_SR=6,MAX_BDL_ENTRIES=32,DMA_ENGINE_OFF=0;
struct BD {uint32_t address;uint16_t wLength,policy;};
struct CMiniportStream;
struct CMiniport {CMiniportStream* Streams[3]={};bool Audio207Fault=false;};
static unsigned stalls;
static void KeStallExecutionProcessor(unsigned n){stalls+=n;}
struct CMiniportStream {
    unsigned DMAEngineState=3,Pin=0,reads=0,haltAfter=0,haltReads=0;
    bool unstable=false,allOnes=false;unsigned civ=0,picb=0;CMiniport* Miniport;
    BD table[32]={};BD* BDList=table;
    std::vector<unsigned> writes;
    UCHAR ReadReg8(unsigned r){assert(r==X_CIV);++reads;return unstable?(reads&31):civ;}
    USHORT ReadReg16(unsigned r){if(r==X_SR)return allOnes?0xffff:(haltReads++>=haltAfter?1:0);assert(r==X_PICB);return picb;}
    void WriteReg8(unsigned r,unsigned v){assert(r==X_CR&&v==0);writes.push_back(1);}
    void WriteReg16(unsigned r,unsigned v){assert(r==X_SR&&v==0x1c);writes.push_back(2);}
    void WriteReg32(unsigned r,unsigned v){assert(r==0&&v==0);writes.push_back(3);}
    int GetBuffPos(DWORD*);
    static NTSTATUS Quiesce207(PINTERRUPTSYNC,PVOID);
};
'''
tests=r'''
int main(){
    unsigned tests=0;DWORD position;
    for(unsigned c=0;c<32;c++)for(unsigned p=0;p<=960;p++){
        CMiniportStream s;s.civ=c;s.picb=p;s.table[c].wLength=960;
        assert(s.GetBuffPos(&position)==(int)c&&position==(960-p)*2);++tests;
    }
    for(unsigned c=32;c<256;c++){
        CMiniportStream s;s.civ=c;assert(s.GetBuffPos(&position)==-1&&position==0);++tests;
    }
    {CMiniportStream s;s.unstable=true;assert(s.GetBuffPos(&position)==-1&&s.reads==16);++tests;}
    {CMiniportStream s;s.picb=961;s.table[0].wLength=960;assert(s.GetBuffPos(&position)==-1);++tests;}
    {CMiniportStream s;s.BDList=nullptr;assert(s.GetBuffPos(&position)==-1);++tests;}
    {CMiniportStream s;s.DMAEngineState=0;assert(s.GetBuffPos(&position)==0&&position==0&&!s.reads);++tests;}
    for(unsigned halt=0;halt<=100;halt++){
        CMiniport m;CMiniportStream s;s.Miniport=&m;m.Streams[0]=&s;s.haltAfter=halt;stalls=0;
        auto result=CMiniportStream::Quiesce207(nullptr,&s);
        assert(!m.Streams[0]&&s.DMAEngineState==0&&s.writes[0]==1);
        if(halt<100){assert(result==0&&!m.Audio207Fault&&stalls==halt&&s.writes==std::vector<unsigned>({1,2,3}));}
        else{assert(result==-1&&m.Audio207Fault&&stalls==100&&s.writes.size()==1);}
        ++tests;
    }
    {CMiniport m;CMiniportStream s;s.Miniport=&m;m.Streams[0]=&s;s.allOnes=true;stalls=0;
     assert(CMiniportStream::Quiesce207(nullptr,&s)==-1&&m.Audio207Fault&&!m.Streams[0]&&stalls==100&&s.writes==std::vector<unsigned>({1}));++tests;}
    return tests==31082?0:1;
}
'''
# Existing position/halt cases plus an all-ones MMIO failure.
assert 32*961+224+4+101+1==31082
p=out/'actual-methods.cpp';p.write_text(prefix+body+tests)
subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined',str(p),'-o',str(out/'test')],check=True)
subprocess.run([str(out/'test')],check=True)
(k/'host-tests003.json').write_text(json.dumps(dict(passed=True,cases=31082,scope=__doc__,source_sha256=hashlib.sha256(s.encode()).hexdigest(),test_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),asan=True,ubsan=True,physical_qualified=False),indent=2)+'\n')
print('31082 actual-method MMIO fault cases passed under ASan/UBSan')
