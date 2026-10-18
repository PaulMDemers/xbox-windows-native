"""Prepare actual post-stack stub execution with modeled privileged interfaces."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;b=json.loads((K/'build001.json').read_text())
t=(K.parent/'entry-marker465/test.c').read_text()
model=t[t.index('static int mode,stage'):t.index('static void trap(')]
source='''#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/prctl.h>
#include <sys/mman.h>
#include <setjmp.h>
#include <ucontext.h>
static sigjmp_buf done;
static unsigned expected_result;
static uint32_t *record;
extern void enter_stub(void);
'''+model+'''
static void trap(int sig,siginfo_t *info,void *v) {
    (void)info;assert(sig==SIGSEGV);
    ucontext_t *u=v;greg_t *g=u->uc_mcontext.gregs;
    if((uint32_t)g[REG_EIP]==0x26000f5) {
        assert(record[5]==1 && expected_result==1);
        assert((uint32_t)g[REG_EAX]==0x11111111 && (uint32_t)g[REG_EBX]==0x22222222);
        assert((uint32_t)g[REG_ECX]==0x33333333 && (uint32_t)g[REG_EDX]==0x44444444);
        assert((uint32_t)g[REG_ESI]==0x55555555 && (uint32_t)g[REG_EDI]==0x66666666);
        assert((uint32_t)g[REG_EBP]==0x77777777 && (uint32_t)g[REG_ESP]==0x2800000);
        assert(((uint32_t)g[REG_EFL]&0xed5)==0xed5);
        siglongjmp(done,1);
    }
    unsigned char *p=(void *)(uintptr_t)g[REG_EIP];
    unsigned port=(unsigned)g[REG_EDX]&0xffff;
    if(p[0]==0xfa) {cli_seen++;g[REG_EIP]++;return;}
    if(p[0]==0xf4) {assert(record[5]==expected_result && expected_result!=1);siglongjmp(done,2);}
    if(p[0]==0x0f && p[1]==0x31) {
        uint64_t t=tick();g[REG_EAX]=(uint32_t)t;g[REG_EDX]=(uint32_t)(t>>32);g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xed) {
        assert(port==0xc000);g[REG_EAX]=(g[REG_EAX]&0xffff0000u)|status();g[REG_EIP]+=2;return;
    }
    if(p[0]==0x66 && p[1]==0xef) {output(port,(unsigned)g[REG_EAX]&0xffff,2);g[REG_EIP]+=2;return;}
    if(p[0]==0xee) {output(port,(unsigned)g[REG_EAX]&0xff,1);g[REG_EIP]++;return;}
    fprintf(stderr,"unexpected stub fault %p %02x mode%d\\n",(void*)p,p[0],mode);abort();
}
int main(int argc,char **argv) {
    assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);
    unsigned char blob[4096];size_t n=fread(blob,1,sizeof(blob),f);assert(n>100 && n<4096 && feof(f));fclose(f);
    assert(mmap((void*)0x2680000,4096,7,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x2680000);
    assert(mmap((void*)0x27f0000,65536,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x27f0000);
    assert(mmap((void*)0x2600000,4096,0,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x2600000);
    stack_t ss={0};ss.ss_size=65536;ss.ss_sp=malloc(ss.ss_size);assert(ss.ss_sp);assert(!sigaltstack(&ss,NULL));
    struct sigaction sa={0};sa.sa_sigaction=trap;sa.sa_flags=SA_SIGINFO|SA_ONSTACK;
    assert(!sigaction(SIGSEGV,&sa,NULL));assert(!prctl(PR_SET_TSC,PR_TSC_SIGSEGV,0,0,0));
    static const unsigned results[32]={1,1,3,4,5,5,3,4,5,6,6,6,6,7,3,4,5,5,5,1,1,5,1,2,2,2,2,2,2,7,6,1};
    unsigned cases=0;
    for(mode=0;mode<32;mode++) {
        if(mode>=23 && mode<=28)continue;
        memcpy((void*)0x2680000,blob,n);memset((void*)0x27f0000,0xa7,65536);
        record=(void*)RECORD_ADDRESS;expected_result=results[mode];stage=2;
        active=starts=writes=reads=tscs=cli_seen=config_step=0;idle_reads=completion_reads=0;sticky=mode==1?0x10:0;
        int stopped=sigsetjmp(done,1);if(!stopped)enter_stub();
        assert(stopped==(expected_result==1?1:2));
        assert(record[5]==expected_result && record[22]==1 && record[3]==2 && record[4]==0xa5);
        assert(record[9]<=4096 && record[19]<=10 && record[23]==0);
        for(unsigned i=0;i<65000;i++)assert(*((unsigned char*)0x27f0000+i)==0xa7);
        char name[40];snprintf(name,sizeof(name),"stub%02d.bin",mode);FILE *o=fopen(name,"wbx");assert(o);assert(fwrite(record,1,96,o)==96);fclose(o);
        cases++;
    }
    printf("PASS %u actual post-stack stub cases; port/CLI/TSC modeled; original stack installation and success register preservation verified\\n",cases);
    return 0;
}
'''
source=source.replace('RECORD_ADDRESS',str(b['stub_symbols']['after_stack_record']))
assert not (K/'test-stub.c').exists();(K/'test-stub.c').write_text(source)
(K/'enter-stub.S').write_text('''.intel_syntax noprefix
.code32
.text
.global enter_stub
enter_stub:
 push 0xed7
 popfd
 mov eax,0x11111111
 mov ebx,0x22222222
 mov ecx,0x33333333
 mov edx,0x44444444
 mov esi,0x55555555
 mov edi,0x66666666
 mov ebp,0x77777777
 mov esp,0xdead0000
 jmp 0x2680000
.section .note.GNU-stack,"",@progbits
''')
r=(K/'host001.py').read_text().replace('host001','stub-host001').replace('test-wrapper.c','test-stub.c').replace('test-wrapper','test-stub').replace("B/'default.xbe'","B/'stub.bin'")
r=r.replace("==build['sha256']","==build['files'][str(B/'stub.bin')]['sha256']")
r=r.replace("O.mkdir();shutil.copyfile(K/'test-stub.c',O/'test-stub.c')","O.mkdir();shutil.copyfile(K/'test-stub.c',O/'test-stub.c');shutil.copyfile(K/'enter-stub.S',O/'enter-stub.S')")
r=r.replace("'test-stub.c','-o'","'test-stub.c','enter-stub.S','-o'").replace("O/'test-stub.c',B/","O/'test-stub.c',O/'enter-stub.S',B/")
r=r.replace('57 actual-wrapper','26 actual post-stack stub').replace('cases=57','cases=26')
(K/'stub-host001.py').write_text(r)
(K/'StubHost001.ps1').write_text((K/'Host001.ps1').read_text().replace('host001.py','stub-host001.py'))
