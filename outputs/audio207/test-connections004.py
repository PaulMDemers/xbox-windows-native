"""Actual source connections must never reference absent render-only filter pins."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[1]);d=src/'drivers/wdm/audio/drivers/ac97'
old=k/'artifacts/source002-before003';out=k/'artifacts/connection-tests004';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k/'source-build002.json').read_text())['sources']
assert all(sha(old/n)==pins[n] for n in ['adapter.cpp','mintopo.cpp'])
def function(s,start):
    a=s.index(start);b=s.index('{',a);depth=1;i=b+1
    while depth:
        depth+=(s[i]=='{')-(s[i]=='}');i+=1
    return s[a:i]
prefix=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#define XBOX_NT5_AC97_MMIO 1
#define PAGED_CODE() ((void)0)
#define DOUT(...) ((void)0)
#define ASSERT(x) assert(x)
#define STDMETHODIMP NTSTATUS
#define OUT
#define NT_SUCCESS(x) ((x)>=0)
using ULONG=uint32_t;using PULONG=ULONG*;using NTSTATUS=int;
const int STATUS_SUCCESS=0,STATUS_INVALID_PARAMETER=-1;
const int PIN_WAVEOUT_SOURCE=0,PIN_WAVEIN_DEST=1,PIN_MICIN_DEST=2,PINC_MICIN_PRESENT=1;
const int PIN_WAVEOUT_BRIDGE=1,PIN_WAVEIN_BRIDGE=3,PIN_MICIN_BRIDGE=5;
struct Common {bool mic;bool GetPinConfig(int p){assert(p==PINC_MICIN_PRESENT);return mic;}};
static int deviceObject,waveObject,topologyObject;
struct Connection {void* from;ULONG fromPin;void* to;ULONG toPin;};
static std::vector<Connection> calls;static bool failRender;
static NTSTATUS PcRegisterPhysicalConnection(void* device,void* from,ULONG fromPin,void* to,ULONG toPin){
 assert(device==&deviceObject);calls.push_back({from,fromPin,to,toPin});
 return failRender||fromPin>=2||toPin>=2?STATUS_INVALID_PARAMETER:STATUS_SUCCESS;
}
'''
body=''
for label,root in [('Old',old),('New',d)]:
    topo=(root/'mintopo.cpp').read_text();adapter=(root/'adapter.cpp').read_text()
    assert 'FilterDescriptor->PinCount = 2;' in topo
    f=function(topo,'STDMETHODIMP CAC97MiniportTopology::GetPhysicalConnectionPins')
    a=adapter.index('        // register wave render connection\n');b=adapter.index('\n    }\n\n    //\n    // Release the adapter',a)
    body+='namespace '+label+r''' {
struct CAC97MiniportTopology {
 Common* AdapterCommon;
 ULONG TransPinDefToPinNr(int pin){return pin==PIN_WAVEOUT_SOURCE?0:ULONG(-1);}
 NTSTATUS GetPhysicalConnectionPins(PULONG,PULONG,PULONG);
};
'''+f+r'''
NTSTATUS connect(bool microphone){
 Common common{microphone};Common* pAdapterCommon=&common;CAC97MiniportTopology topo{&common};
 ULONG ulWaveOut=99,ulWaveIn=99,ulMicIn=99;
 void* DeviceObject=&deviceObject;void* unknownWave=&waveObject;void* unknownTopology=&topologyObject;
 NTSTATUS ntStatus=topo.GetPhysicalConnectionPins(&ulWaveOut,&ulWaveIn,&ulMicIn);
'''+adapter[a:b]+'\nreturn ntStatus;\n}\n}\n'
tests=r'''
int main(){unsigned cases=0;
 for(bool mic: {false,true}){
  calls.clear();failRender=false;assert(New::connect(mic)==0&&calls.size()==1);
  assert(calls[0].from==&waveObject&&calls[0].fromPin==1&&calls[0].to==&topologyObject&&calls[0].toPin==0);++cases;
  calls.clear();int old=Old::connect(mic);
  if(mic){assert(old<0&&calls.size()==2&&calls[1].fromPin==ULONG(-1)&&calls[1].toPin==5);}
  else{assert(old==0&&calls.size()==1);}++cases;
  calls.clear();failRender=true;assert(New::connect(mic)<0&&calls.size()==1);++cases;
 }
 assert(cases==6);return 0;
}
'''
p=out/'actual-connections.cpp';p.write_text(prefix+body+tests)
subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined',str(p),'-o',str(out/'test')],check=True)
subprocess.run([str(out/'test')],check=True)
r=dict(passed=True,cases=6,scope=__doc__,adapter_sha256=sha(d/'adapter.cpp'),topology_sha256=sha(d/'mintopo.cpp'),test_sha256=sha(p),asan=True,ubsan=True,limits='Old source reproduces an out-of-range microphone connection under a rejecting mock; this does not prove the actual NT5 failure cause or physical behavior')
(k/'connection-tests004.json').write_text(json.dumps(r,indent=2)+'\n');print('Six actual-source physical-connection cases passed; old invalid-pin request reproduced')
