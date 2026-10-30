"""Actual retention/map logic tests with substituted I/O; compiled call-path audit."""
import datetime,hashlib,json,os,re,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/home/paul/xbox-windows-native/boot720836-source001');O=Path('/mnt/c/xwn836/qualify001');assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists();O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'physical_access':False,'scope':'Actual C retention and map-validation logic with substituted register reads, mapped MMIO and stop traps. Binary call-path audit. No encoder or hardware emulation.'}
try:
 chain=json.loads((K/'chain002.json').read_text());assert chain['passed'];r['chain_record_sha256']=sha(K/'chain002.json')
 for n,v in chain['artifacts'].items():assert sha(O.parent/'chain002'/n)==v['sha256']
 s=(K/'retain835.c').read_text();assert (B/'cromwell/boot/retain835.c').read_text()==s;r['retention_source_sha256']=sha(K/'retain835.c')
 s=re.sub(r'^#include.*\n','',s,flags=re.M)
 a=s.index('static unsigned char cr(');b=s.index('static void stop835(',a)
 s=s[:a]+'static unsigned char cr(unsigned i) { return crt[i]; }\n'+s[b:]
 s=s.replace('static void stop835(void) { __asm__ volatile("cli");for(;;)__asm__ volatile("hlt"); }','static void stop835(void) { longjmp(trap,1); }')
 prefix='''#define _GNU_SOURCE
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#define RAMSIZE 0x04000000
#define FB_SIZE 0x00900000
#define FB_START 0xf3700000
#define MAX_INITRD_END 0x03700000
#define ENCODER_XCALIBUR 2
static unsigned xbox_ram,video_encoder;static unsigned char VIDEO_AV_MODE,crt[256];static jmp_buf trap;
typedef struct {unsigned m_dwFrameBufferStart;void *m_pbBaseAddressVideo;unsigned m_bBPP,width,height,xmargin,ymargin,m_bAvPack;} CURRENT_VIDEO_MODE_DETAILS;
'''
 suffix='''
#define MM(o) (*(volatile unsigned *)(uintptr_t)(0xfd000000u+(o)))
static void init(void){memset((void *)0xfd000000,0,0x700000);memset(crt,0,sizeof(crt));
 MM(0x680838)=1279;MM(0x680818)=719;MM(0x600800)=0x03c5c000;MM(0x100200)=0x03070003;
 MM(0x140)=1;MM(0x600140)=1;crt[0x13]=0x80;crt[0x19]=0x40;crt[0x28]=3;crt[0x39]=255;xbox_ram=64;}
int main(void){assert(mmap((void *)0xfd000000,0x700000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0)==(void *)0xfd000000);
 unsigned cases=0;CURRENT_VIDEO_MODE_DETAILS m;
 init();assert(!setjmp(trap));XwnRetain720Entry835();assert(!MM(0x140)&&!MM(0x600140));
 assert(MM(0x600800)==0x03c5c000);XwnRetain720Mode835(&m);
 assert(MM(0x600800)==0x03700000&&MM(0x100200)==0x03070003&&m.width==1280&&m.height==720&&m.m_bBPP==32&&m.m_dwFrameBufferStart==FB_START);cases++;
 for(unsigned i=0;i<10;i++){init();switch(i){
 case 0:MM(0x680838)=639;break;case 1:MM(0x680818)=479;break;case 2:crt[0x13]=0;break;
 case 3:crt[0x19]=0;break;case 4:crt[0x28]=2;break;case 5:crt[0x39]=0;break;
 case 6:MM(0x600800)=0;break;case 7:MM(0x600800)++;break;case 8:MM(0x600800)=0x027ff000;break;case 9:MM(0x600800)=0x03fff000;break;}
 if(!setjmp(trap)){XwnRetain720Entry835();assert(0);}assert(MM(0x140)==1&&MM(0x600140)==1);cases++;}
 for(unsigned i=0;i<3;i++){init();XwnRetain720Entry835();if(i==0)MM(0x100200)^=0x100;else if(i==1)xbox_ram=128;else MM(0x680838)=639;
 if(!setjmp(trap)){XwnRetain720Mode835(&m);assert(0);}assert(MM(0x600800)==0x03c5c000);cases++;}
 printf("PASS %u retained720 logic cases\\n",cases);return 0;}
'''
 (O/'retain-test.c').write_text(prefix+s+suffix)
 mem=B/'reactos/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c';t=mem.read_text();r['mem_source_sha256']=sha(mem)
 a=t.index('VOID\nXboxMemInit(VOID)');b=t.index('\nmemory_map_t *\nXboxGetMultibootMemoryMap',a);fn=t[a:b]
 h=B/'reactos/sdk/include/reactos/drivers/xbox/xwn_hd_layout.h';r['layout_header_sha256']=sha(h)
 mp='''#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#define XWN_RETAIN_720_835 1
#define VOID void
typedef int INT;typedef unsigned ULONG;
typedef struct {unsigned base_addr_low,base_addr_high,length_low,length_high,type;} memory_map_t;
static memory_map_t rows[2];static int count,missing,pci;static unsigned InstalledMemoryMb,AvailableMemoryMb;static jmp_buf trap;
static memory_map_t *XboxGetMultibootMemoryMap(int *n){*n=count;return missing?0:rows;}
static void XboxInitializePCI(void){pci++;}
static void FrLdrBugCheckWithMessage(int a,const char*b,int c,const char*d){(void)a;(void)b;(void)c;(void)d;longjmp(trap,1);}
'''
 mt='''
static void init(void){rows[0]=(memory_map_t){0,0,0x03700000,0,1};rows[1]=(memory_map_t){0x03700000,0,0x00900000,0,0};count=2;missing=0;pci=0;InstalledMemoryMb=AvailableMemoryMb=0;}
int main(void){unsigned cases=0;init();assert(!setjmp(trap));XboxMemInit();assert(InstalledMemoryMb==64&&AvailableMemoryMb==64&&pci==1);cases++;
 for(unsigned i=0;i<13;i++){init();if(i==0)missing=1;else if(i==1)count=1;else if(i==2)count=3;else ((unsigned *)rows)[i-3]^=1;
 if(!setjmp(trap)){XboxMemInit();assert(0);}assert(!InstalledMemoryMb&&!AvailableMemoryMb&&!pci);cases++;}
 printf("PASS %u retail64 map cases\\n",cases);return 0;}
'''
 (O/'map-test.c').write_text(mp+h.read_text()+fn+mt)
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['tests']={}
 for name in ['retain','map']:
  cmd=[str(cc),'-O1','-Wall','-Wextra','-Wno-int-to-pointer-cast','-fsanitize=undefined',str(O/(name+'-test.c')),'-o',str(O/name)]
  v=subprocess.run(cmd,capture_output=True,timeout=45);(O/(name+'-build.log')).write_bytes(v.stdout+v.stderr);assert v.returncode==0,v.stderr.decode()
  v=subprocess.run([str(O/name)],capture_output=True,timeout=10);(O/(name+'-run.log')).write_bytes(v.stdout+v.stderr);assert v.returncode==0,v.stderr.decode();r['tests'][name]=v.stdout.decode().strip()
 dis=(O.parent/'chain002/disassembly.txt').read_text();a=dis.index('<BootResetAction>:');b=dis.index('\n\n',a);body=dis[a:b]
 calls=re.findall(r'call\s+[^<]+<([^>]+)>',body);r['startup_calls']=calls
 assert all(n not in calls for n in ['BootVgaInitializationKernelNG','BootAGPBUSInitialization','BootDetectMemorySize'])
 assert all(n in calls for n in ['XwnRetain720Entry835','XwnRetain720Mode835','BootPciPeripheralInitialization','BootEepromReadEntireEEPROM','BootIdeInit','BootFromDevice'])
 # Confirm the actual FreeLoader object compiled the retained branch, not the128M path.
 obj=B/'nt5/boot/freeldr/freeldr/CMakeFiles/freeldr_common.dir/arch/i386/xbox/xboxmem.c.obj'
 d=subprocess.check_output(['objdump','-dr',str(obj)],text=True);(O/'xboxmem-disassembly.txt').write_text(d)
 a=d.index('<_XboxMemInit>:');b=d.find('\n\n',a);body=d[a:b]
 assert '0x3070103' not in body and '0x11448000' not in body and '0x7ffffff' not in body
 assert '_XboxGetMultibootMemoryMap' in body and '_FrLdrBugCheckWithMessage' in body
 r['compiled_retained_branch']=True;r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['files']={p.name:sha(p) for p in O.iterdir() if p.is_file()};r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (K/'qualify001.json').write_text(json.dumps(r,indent=2)+'\n')
print(r.get('tests'), 'compiled retained branch:',r['passed'])
