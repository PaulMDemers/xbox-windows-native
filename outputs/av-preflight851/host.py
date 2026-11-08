from pathlib import Path
import re, subprocess, tempfile, json, hashlib
p=Path(__file__).resolve().parent;s=(p/'main.c').read_text()
for term in ['XVideoSetMode','HalWriteSMBusValue','NtSetSystemInformation','XVideoSetEncoderSettings']: assert term not in s,term
assert all(x in s for x in ['CREATE_NEW','NtFlushBuffersFile','memcmp(report, verify, used)','HalReturnToFirmware(HalRebootRoutine)'])
m=re.search(r'int memory_ok=.*?;\n    int pack_ok=.*?;\n    int sdk_480=.*?;\n    int raw_480=.*?;',s,re.S); assert m
h='''#include <assert.h>\n#define VIDEO_ADAPTER_MASK 255\n#define AV_PACK_HDTV 4\n#define VIDEO_MODE_480P 0x80000\nint f(unsigned settings,int ms,unsigned pages,int fs,unsigned flags){ struct {unsigned TotalPhysicalPages;} memory={pages};\n'''+m.group()+'''\nreturn memory_ok | pack_ok<<1 | sdk_480<<2 | raw_480<<3;}\nint main(void){ for(unsigned flags=0;flags<256;flags++) for(unsigned a=0;a<8;a++) for(unsigned e=0;e<2;e++) for(unsigned ok=0;ok<2;ok++) { unsigned settings=a|(e?0x80000:0);int got=f(settings,ok?0:-1,ok?16384:0,ok?0:-1,flags); int want=ok|((a==4)<<1)|(e<<2)|((ok&&((flags&8)!=0))<<3);assert(got==want);}return 0;}\n'''
with tempfile.TemporaryDirectory() as d:
 c=Path(d)/'t.c';c.write_text(h);exe=Path(d)/'t';subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
r={'passed':True,'cases':8192,'scope':'Compiled source expressions for kernel settings, EEPROM raw bit and memory predicates; exclusive-create/flush/readback/reboot calls statically checked. Kernel SMBus, storage and physical console are not simulated.','source_sha256':hashlib.sha256(s.encode()).hexdigest()};(p/'host001.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
