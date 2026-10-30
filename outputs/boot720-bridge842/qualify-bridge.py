"""Execute exact restored bridge block with substituted PCI access; no hardware."""
from pathlib import Path
import hashlib,json,os,re,subprocess
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720842-source001');O=Path('/mnt/c/xwn842/bridge001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'scope':'Actual restored bridge block and readback predicate with substituted PCI functions; no hardware qualification'}
try:
 source=B/'cromwell/drivers/pci/pci.c';s=source.read_text();a=s.index('// Bus 0, Device 1e, Function 0 = nForce AGP Host to PCI Bridge');b=s.index('#ifndef XWN_RETAIN_720_835',a);block=s[a:b]
 old=Path('/home/paul/xbox-windows-native/boot720841-source002/cromwell/drivers/pci/pci.c').read_text();oa=old.index('// Bus 0, Device 1e, Function 0 = nForce AGP Host to PCI Bridge');ob=old.index('// Bus 1, Device 0, Function 0 = NV2A',oa)
 assert block.strip()==old[oa:ob].strip()
 startup=(B/'cromwell/boot/BootResetAction.c').read_text();a=startup.index('if (PciReadDword(0,30,0,0x20)');b=startup.index(' {',a);predicate=startup[a+4:b-1]
 stub=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef unsigned u32;
#define BUS_0 0
#define DEV_1e 30
#define FUNC_0 0
static unsigned reg[16],writes,offsets[16];
static unsigned PciReadDword(unsigned bus,unsigned dev,unsigned fn,unsigned off){assert(bus==0&&dev==30&&fn==0&&!(off&3)&&off<64);return reg[off/4];}
static void PciWriteDword(unsigned bus,unsigned dev,unsigned fn,unsigned off,unsigned v){assert(bus==0&&dev==30&&fn==0&&!(off&3)&&off<64);assert(writes<16);offsets[writes++]=off;reg[off/4]=v;}
'''
 test=r'''
int main(void){unsigned cases=0;
for(unsigned bits=0;bits<8;bits++){
 memset(reg,0,sizeof(reg));reg[1]=0x02200000|bits;reg[6]=0x00010177;reg[9]=0xf3f0f000;writes=0;
 bridge();assert(writes==13&&reg[1]==0x02200007&&reg[6]==0x00010100&&reg[15]==7);
 assert(reg[8]==0xfdf0fd00&&reg[9]==0xf7f0f000&&reg[3]==0xff019ee7);assert(ready());cases++;
 unsigned expected[]={4,0x18,0x3c,0x0c,0x10,0x14,0x1c,0x20,0x24,0x28,0x2c,0x30,0x38};assert(!memcmp(offsets,expected,sizeof(expected)));cases++;
}
unsigned bad[]={0x20,0x24,0x18,0x3c};
for(unsigned i=0;i<4;i++){unsigned save=reg[bad[i]/4];reg[bad[i]/4]^=0x100;assert(!ready());reg[bad[i]/4]=save;cases++;}
printf("PASS %u exact bridge setup/readback cases;13 writes all00:1e.0\n",cases);return 0;}
'''
 (O/'test.c').write_text(stub+'\nstatic void bridge(void){\n'+block+'\n}\nstatic int ready(void){return !('+predicate+');}\n'+test)
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 p=subprocess.run([str(cc),'-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(O/'test.c'),'-o',str(O/'test')],capture_output=True,timeout=60);(O/'build.log').write_bytes(p.stdout+p.stderr);assert not p.returncode,p.stderr.decode()
 p=subprocess.run([str(O/'test')],capture_output=True,timeout=15);(O/'run.log').write_bytes(p.stdout+p.stderr);assert not p.returncode,p.stderr.decode();r['result']=p.stdout.decode()
 # Preprocess actual PCI file without headers; types are irrelevant for -E.
 text=re.sub(r'^#include.*$','',s,flags=re.M)
 p=subprocess.run([str(cc),'-E','-P','-DXWN_RETAIN_720_835=1','-x','c','-'],input=text,text=True,capture_output=True,check=True,timeout=15)
 body=p.stdout[p.stdout.index('void BootPciPeripheralInitialization'):];assert 'PciWriteDword(BUS_1' not in body and '0xf7f0f000' in body
 r['retained_gpu_config_excluded']=True;r['restored_block_matches_existing_initializer']=True;r['pci_source_sha256']=sha(source);r['startup_source_sha256']=sha(B/'cromwell/boot/BootResetAction.c');r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};(K/'bridge001.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['result'])
