"""Generate a new full-wrapper integration harness from frozen487; no launch."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'blend-precision487/test-wrapper002.c';O=K/'full-wrapper001.c'
assert not O.exists()
s=P.read_text().replace('487','490').replace('0x37383458','0x30393458').replace('0x37383452','0x30393452')
def change(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change('static int new_success;', '''static int new_success;
static int cmode,cc,cw,cf,ccl,capcalls;
static unsigned char context_bytes[400];
static unsigned context_size;
''')
change('static void save_witness(void) {', '''static void save_witness(void) {
    char cn[48];snprintf(cn,sizeof(cn),"context%03d.bin",case_id);
    FILE *cx=fopen(cn,"wbx");assert(cx);assert(fwrite(context_bytes,1,context_size,cx)==context_size);fclose(cx);
''')
change('    creates++;\n    const char *expected=', '''    const char *cp="\\\\Device\\\\Harddisk0\\\\Partition1\\\\Applications\\\\XWNBoot490a\\\\context.bin";
    if(!strcmp((char*)*ptr,cp)) {
        cc++;assert(cc==1 && wc==1 && ww==1 && wf==1 && wcl==1 && capcalls==2);
        assert(name[0]==strlen(cp) && name[1]==name[0]+1);
        if(cmode==1)return 0xc0000035u;
        if(cmode==2)return 0x103;
        *handle=cmode==6?0:0x4903;
        if(cmode==4)return 0;
        iosb[0]=cmode==3?0xc0000185u:0;iosb[1]=cmode==5?1:2;return 0;
    }
    creates++;
    const char *expected=''')
change('    writes++;\n    assert(handle==0x4780', '''    if(handle==0x4903) {
        cw++;assert(cw==1 && cc==1 && bytes==400 && !event && !apc && !ctx && !offset);
        assert(*(const uint32_t*)buf==0x30393443 && ((const uint32_t*)buf)[6]==2);
        if(cmode==7)return 0xc0000185u;
        context_size=cmode==11?399:400;memcpy(context_bytes,buf,context_size);
        if(cmode==10)return 0;
        iosb[0]=cmode==9?0xc0000185u:0;iosb[1]=cmode==12?401:context_size;
        return cmode==8?0x103:0;
    }
    writes++;
    assert(handle==0x4780''')
change('    flushes++;assert(handle==0x4780);', '''    if(handle==0x4903) {
        cf++;assert(cf==1 && cw==1);
        if(cmode==16)return 0;
        iosb[0]=cmode==15?0xc0000185u:0;iosb[1]=0;
        return cmode==13?0xc0000185u:cmode==14?0x103:0;
    }
    flushes++;assert(handle==0x4780);''')
change('    closes++;assert(handle==0x4780);', '''    if(handle==0x4903) {
        ccl++;assert(ccl==1);
        return cmode==17?0xc0000185u:cmode==18?0x103:0;
    }
    closes++;assert(handle==0x4780);''')
change('    assert(sig==SIGSEGV && u->uc_mcontext.gregs[REG_TRAPNO]==13);', '''    if(sig==SIGTRAP) {
        /* Explicit debugger substitution in THIS full-wrapper harness only.
         * Actual identical privileged capture instructions were exercised by
         * separate diskless490 host001. This signal path models CPU facts. */
        greg_t *g=u->uc_mcontext.gregs;
        assert((uint32_t)g[REG_EIP]==CAPTURE_ADDRESS+1 && image[CAPTURE_ADDRESS-0x10000]==0x9c);
        capcalls++;assert(capcalls<=2 && (uint32_t)g[REG_ECX]==160);
        uint32_t *r=(void*)(uintptr_t)g[REG_EDI];
        assert((uint32_t)r==(capcalls==1?FIRST_ADDRESS:SECOND_ADDRESS));
        assert(r[0]==0x39383443 && r[1]==1 && r[2]==160 && r[3]==(unsigned)capcalls && r[4]==0x48900101 && !r[33]);
        r[5]=g[REG_EFL];r[6]=r[24]=0x80000011;r[7]=r[25]=capcalls==1?0x12345000:0x6789a000;
        r[8]=r[26]=capcalls==1?0x1000000:0x1002000;r[9]=r[27]=0x10;
        uint16_t *sel=(void*)(r+10);for(unsigned i=0;i<6;i++)sel[i]=i?16:8;
        r[18]=g[REG_ESP];r[19]=*(uint32_t*)(uintptr_t)g[REG_ESP];r[20]=10000000u+capcalls*1000;r[22]=r[20]+10;
        r[38]=0x454e4f44;r[39]=0x48900101;r[33]=1;
        g[REG_EIP]=r[19];g[REG_ESP]+=4;return;
    }
    assert(sig==SIGSEGV && u->uc_mcontext.gregs[REG_TRAPNO]==13);''')
change('    assert(wc==1 && ww==1 && wf==1 && wcl==1 && witness_size==256);','''    assert(wc==1 && ww==1 && wf==1 && wcl==1 && witness_size==256);
    assert(cc==1 && cw==1 && cf==1 && ccl==1 && context_size==400 && capcalls==2);''')
change('assert(!sigaction(SIGSEGV,&sa,0));','assert(!sigaction(SIGSEGV,&sa,0));assert(!sigaction(SIGTRAP,&sa,0));')
change('case_id<132','case_id<150')
change('        active=starts=port_writes=port_reads=tscs=cli_seen=config_step=0;', '''        cmode=case_id>=132?case_id-131:0;cc=cw=cf=ccl=capcalls=0;context_size=0;memset(context_bytes,0,sizeof(context_bytes));
        if(case_id>=132){pmode=fmode=mode=wmode=new_success=0;}
        active=starts=port_writes=port_reads=tscs=cli_seen=config_step=0;''')
change('memcpy((void*)0x10000,image,image_size);','memcpy((void*)0x10000,image,image_size);*(unsigned char*)CAPTURE_ADDRESS=0xcc;')
change('        if(case_id>=104) {\n            clear_df();', '''        if(case_id>=132) {
            clear_df();assert(!handoffs && fc==1 && fallback_size==192 && fcl==1);
            assert(creates==1 && writes==2 && flushes==2 && closes==1 && wc==1 && ww==1 && wf==1 && wcl==1);
            unsigned op=cmode<=6?0:cmode<=12?1:cmode<=16?2:3;
            unsigned reason=22+op;const uint32_t *q=(void*)fallback;
            assert(q[4]==reason && q[8]==(cmode==1||cmode==2||cmode==6?0:0x4903));
            assert(q[9]==(op==3?1:0));
            assert(cc==1 && cw==(op>=1) && cf==(op>=2));
            assert(ccl==!(cmode==1 || cmode==2 || cmode==6));
            assert(context_size==(cmode<=7?0:cmode==11?399:400));
            save_witness();char fn[48];snprintf(fn,sizeof(fn),"contextrefusal%03d.bin",case_id);
            FILE *nf=fopen(fn,"wbx");assert(nf);assert(fwrite(fallback,1,192,nf)==192);fclose(nf);
            printf("context case=%d reason=%u calls=%d/%d/%d/%d bytes=%u\\n",case_id,reason,cc,cw,cf,ccl,context_size);
            cases++;continue;
        }
        if(case_id>=104) {
            clear_df();''')
change('q[8]==((wmode==1 || wmode==2 || wmode==6)?0:0x4902)','q[8]==((wmode==1 || wmode==2 || wmode==6)?0:reason>=17?0x4903:0x4902)')
change('kernel/file/SMBus/TSC effects modeled; loader CLI trapped before execution','kernel/file/SMBus/TSC/CPU capture effects modeled; capture entry replaced by debugger trap; loader CLI trapped before execution')
O.write_text(s)
(K/'full-source001.json').write_text(json.dumps(dict(parent_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(O.read_bytes()).hexdigest(),generated=True,physical_access=False,model_capture=True,actual_privileged_capture_separate='host-run001.json'),indent=2)+'\n')
