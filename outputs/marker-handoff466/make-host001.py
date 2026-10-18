"""Prepare new integration tests without altering any executed predecessor."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
b=json.loads((K/'build001.json').read_text())
p=(K.parent/'boot-refusal462/test-wrapper.c').read_text()
p=p.replace('462','466').replace('0x323634','0x363634').replace('288316',str(b['payload_bytes']))
def sub(old,new):
 global p
 assert p.count(old)==1,old
 p=p.replace(old,new)
sub('#include <ucontext.h>','#include <ucontext.h>\n#include <sys/prctl.h>')
model=(K.parent/'entry-marker465/test.c').read_text()
model=model[model.index('static int mode,stage'):model.index('static void trap(')]
sub('static void trap(',model+'\nstatic void trap(')
sub('    assert((uint32_t)u->uc_mcontext.gregs[REG_EIP]==0x1000000);','''    greg_t *g=u->uc_mcontext.gregs;
    unsigned char *p=(void *)(uintptr_t)g[REG_EIP];
    unsigned port=(unsigned)g[REG_EDX]&0xffff;
    if((uint32_t)g[REG_EIP]!=0x1000000) {
        if(p[0]==0xfa) {cli_seen++;g[REG_EIP]++;return;}
        if(p[0]==0x0f && p[1]==0x31) {
            uint64_t t=tick();g[REG_EAX]=(uint32_t)t;g[REG_EDX]=(uint32_t)(t>>32);g[REG_EIP]+=2;return;
        }
        if(p[0]==0x66 && p[1]==0xed) {
            assert(port==0xc000);g[REG_EAX]=(g[REG_EAX]&0xffff0000u)|status();g[REG_EIP]+=2;return;
        }
        if(p[0]==0x66 && p[1]==0xef) {output_port(port,(unsigned)g[REG_EAX]&0xffff,2);g[REG_EIP]+=2;return;}
        if(p[0]==0xee) {output_port(port,(unsigned)g[REG_EAX]&0xff,1);g[REG_EIP]++;return;}
        fprintf(stderr,"unexpected integration fault %p %02x %02x\\n",(void*)p,p[0],p[1]);abort();
    }''')
# Resolve model variable/function names against inherited file-I/O counters.
p=p.replace('static void output(unsigned','static void output_port(unsigned')
start=p.index('static int mode,stage');end=p.index('static void trap(',start)
segment=p[start:end].replace('writes','port_writes').replace('reads','port_reads')
p=p[:start]+segment+p[end:]
p=p.replace('0x60000,7','0xa0000,7')
sub('    unsigned cases=0;','    assert(prctl(PR_SET_TSC,PR_TSC_SIGSEGV,0,0,0)==0);\n    unsigned cases=0;')
sub('case_id<55','case_id<57')
sub('pmode=case_id>=45?32:case_id;','pmode=case_id>=55?0:case_id>=45?32:case_id;')
sub('        allocs=physcalls=', '''        mode=case_id==55?2:case_id==56?4:0;stage=1;
        active=starts=port_writes=port_reads=tscs=cli_seen=config_step=0;
        idle_port_reads=completion_port_reads=0;sticky=0;
        allocs=physcalls=''')
sub('assert(handoffs==(pmode==0 || pmode==12));','assert(handoffs==((pmode==0 || pmode==12) && case_id<55));')
sub('assert(fc==!(pmode==0 || pmode==12));','assert(fc==!((pmode==0 || pmode==12) && case_id<55));')
sub('unsigned reason=pmode==5','unsigned reason=case_id>=55?12:pmode==5')
sub('                if(pmode==32)assert(q[5]==0xc0000185u);','''                if(pmode==32)assert(q[5]==0xc0000185u);
                if(case_id>=55)assert(q[5]==(case_id==55?3u:5u) && q[9]==2);''')
sub('        char name[40];',f'''        const uint32_t *marker=(void*){b['wrapper_symbols']['before_marker_record']};
        if(handoffs)assert(marker[5]==1 && marker[6]==2 && marker[7]==3 && marker[22]==1);
        else if(case_id>=55)assert(marker[5]==(case_id==55?3u:5u) && marker[22]==1 && !starts);
        else assert(marker[22]==0 && !cli_seen && !port_reads && !port_writes);
        char name[40];''')
sub('        cases++;',f'''        snprintf(name,sizeof(name),"marker%02d.bin",case_id);
        FILE *mr=fopen(name,"wbx");assert(mr);assert(fwrite(marker,1,96,mr)==96);fclose(mr);
        cases++;''')
p=p.replace('kernel/file effects modeled; CLI trapped before privileged execution','kernel/file/SMBus/TSC effects modeled; loader CLI trapped before execution')
assert not (K/'test-wrapper.c').exists()
(K/'test-wrapper.c').write_text(p)
r=(K.parent/'boot-refusal462/host001.py').read_text().replace('/mnt/e/xwn462','/mnt/c/xwn466').replace("disk_usage('/mnt/e')","disk_usage('/mnt/c')").replace('55','57')
r=r.replace("privileged_loader_executed=False,", "privileged_loader_executed=False,SMBus_TSC_CLI='MODELED',")
(K/'host001.py').write_text(r)
ps=(K/'Build001.ps1').read_text().replace('build001.py','host001.py').replace('Build failed','Host test failed')
(K/'Host001.ps1').write_text(ps)
