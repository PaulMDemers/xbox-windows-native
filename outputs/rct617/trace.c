/* MIT. Bounded process-local paired call/return observer. Synthetic qualification601. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "target_iat.h"
#include "calls.h"
#include "dib_header.h"
#include "phase.h"
#include "lifetime.h"
#include "timing.h"
static TIMING617 timing;
typedef struct {DWORD id;HANDLE h;BOOL held;STACK601 stack;} THREAD;
typedef LB610 BP;
static THREAD threads[64];static BP bp[256];static DWORD bp_count,returns;static HANDLE process,logfile;
typedef LM610 MODULE601;
static MODULE601 modules601[256];static DWORD module_count,seen[17],resolved[17],probe_module;
static const DWORD nargs[17]={0,1,2,9,6,3,1,3,4,1,2,13,0,6,2,1,1};
static DWORD step_id,step_bp,requests,started;static BOOL initial,failed,exited;
static void zero(void *p,DWORD n) {BYTE *b=p;while(n--)*b++=0;}
static void line(const char *s) {DWORD n=lstrlenA(s),w;if(!WriteFile(logfile,s,n,&w,0)||w!=n)failed=TRUE;}
static void event(const char *kind,DWORD a,DWORD b,DWORD c) {
    char s[160];wsprintfA(s,"%s %08lx %08lx %08lx\r\n",kind,a,b,c);line(s);
}
static PHASE605 phase_state;static HANDLE phase_request,phase_ack;
static DWORD phase_caps[2],phase_skipped[2];static BOOL defer_reported;
static BOOL phasecheck605(void) {
    DWORD wait,i,pending=0;int result;
    wait=WaitForSingleObject(phase_request,0);
    if(wait!=WAIT_OBJECT_0&&wait!=WAIT_TIMEOUT)return FALSE;
    for(i=0;i<64;i++)pending+=threads[i].stack.depth;
    result=phase605(&phase_state,wait==WAIT_OBJECT_0,pending);
    if(result<0)return FALSE;
    if(result==1&&!defer_reported){event("PHASE_PENDING",0,pending,seen[11]);defer_reported=TRUE;}
    if(result==2){
        event("PHASE",1,seen[11],phase_skipped[0]);seen[11]=0;
        if(!SetEvent(phase_ack))return FALSE;
    }
    return !failed;
}
static BOOL readmem(DWORD address,void *dest,DWORD n) {
    SIZE_T got=0;return address&&ReadProcessMemory(process,(LPCVOID)address,dest,n,&got)&&got==n;
}
static int dibread604(void*ctx,DIBU address,void*dest,DIBU n) {
    (void)ctx;return readmem(address,dest,n);
}
static BOOL dibobserve604(DWORD id,DWORD address) {
    DIBSNAP d;DWORD i;char s[100];dib_snapshot604(dibread604,0,address,&d);
    wsprintfA(s,"DIB %08lx %08lx %08x %08x %08x %08x",id,address,d.status,d.count,d.stride,d.bytes);line(s);
    for(i=0;i<d.count;i++){wsprintfA(s," %08x",d.words[i]);line(s);}line("\r\n");return !failed;
}
static BOOL bytewrite(DWORD address,BYTE value) {
    DWORD old,ignored;SIZE_T written=0;BYTE readback=0;BOOL ok,restored;
    if(!VirtualProtectEx(process,(LPVOID)address,1,PAGE_EXECUTE_READWRITE,&old))return FALSE;
    ok=WriteProcessMemory(process,(LPVOID)address,&value,1,&written)&&written==1;
    restored=VirtualProtectEx(process,(LPVOID)address,1,old,&ignored);
    return ok&&restored&&FlushInstructionCache(process,(LPCVOID)address,1)&&readmem(address,&readback,1)&&readback==value;
}
static THREAD *thread(DWORD id) {DWORD i;for(i=0;i<64;i++)if(threads[i].id==id)return &threads[i];return 0;}
static BOOL addthread(DWORD id,HANDLE h) {
    DWORD i;if(thread(id))return FALSE;
    for(i=0;i<64;i++)if(!threads[i].id) {
        threads[i].id=id;threads[i].h=h;threads[i].held=FALSE;
        if(step_id&&id!=step_id) {if(SuspendThread(h)==(DWORD)-1)return FALSE;threads[i].held=TRUE;}
        return TRUE;
    }return FALSE;
}
static BOOL holdothers(DWORD id) {
    DWORD i;for(i=0;i<64;i++)if(threads[i].id&&threads[i].id!=id) {
        if(threads[i].held||SuspendThread(threads[i].h)==(DWORD)-1)return FALSE;
        threads[i].held=TRUE;
    }return TRUE;
}
static BOOL releaseothers(void) {
    DWORD i,n;for(i=0;i<64;i++)if(threads[i].held) {
        n=ResumeThread(threads[i].h);if(n==(DWORD)-1||n==0)return FALSE;threads[i].held=FALSE;
    }return TRUE;
}
static BOOL module601(DWORD base) {
    IMAGE_DOS_HEADER d;IMAGE_NT_HEADERS32 n;
    if(!readmem(base,&d,sizeof(d))||d.e_magic!=IMAGE_DOS_SIGNATURE||d.e_lfanew<64||d.e_lfanew>4096)return FALSE;
    if(!readmem(base+d.e_lfanew,&n,sizeof(n))||n.Signature!=IMAGE_NT_SIGNATURE||n.OptionalHeader.Magic!=0x10b)return FALSE;
    if(!load610(modules601,module_count,base,n.OptionalHeader.SizeOfImage))return FALSE;
    modules601[module_count].base=base;modules601[module_count].size=n.OptionalHeader.SizeOfImage;
    modules601[module_count].generation=module_count+1;
    modules601[module_count++].active=TRUE;event("MODULE",base,n.OptionalHeader.SizeOfImage,n.FileHeader.TimeDateStamp);
    event("LIFETIME",base,module_count,n.OptionalHeader.SizeOfImage);return !failed;
}
static DWORD owner601(DWORD address) {
    DWORD i;MEMORY_BASIC_INFORMATION m;
    if(!VirtualQueryEx(process,(LPCVOID)address,&m,sizeof(m))||m.State!=MEM_COMMIT||
        !(m.Protect&(PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY))||
        (m.Protect&(PAGE_GUARD|PAGE_NOACCESS)))return 0;
    for(i=0;i<module_count;i++)if(modules601[i].active&&address>=modules601[i].base&&
        address-modules601[i].base<modules601[i].size&&(DWORD)m.AllocationBase==modules601[i].base)return modules601[i].base;
    return 0;
}
static BOOL unload601(DWORD base) {
    DWORD i,j,pending=0,held=0,found;
    for(i=0;i<64;i++){pending+=threads[i].stack.depth;if(threads[i].held)held++;}
    found=retire610(modules601,module_count,bp,bp_count,base,pending,step_id,held);
    if(!found){event("UNLOAD_REJECT",base,pending,step_id);return FALSE;}
    i=found-1;event("QUIESCENT",base,modules601[i].generation,0);
    for(j=0;j<bp_count;j++)if(!bp[j].retired&&bp[j].generation==modules601[i].generation) {
        bp[j].retired=TRUE;event("RETIRE",j,bp[j].generation,bp[j].address);
    }
    modules601[i].active=FALSE;event("UNLOAD",base,0,0);return !failed;
}
static BOOL addbp(DWORD address,DWORD api,DWORD *index) {
    DWORD i,owner,generation=0;BYTE original;char msg[160];
    if(!address)return FALSE;
    owner=owner601(address);if(!owner)return FALSE;
    for(i=0;i<module_count;i++)if(modules601[i].active&&modules601[i].base==owner)generation=modules601[i].generation;
    if(!generation)return FALSE;
    for(i=0;i<bp_count;i++)if(!bp[i].retired&&bp[i].address==address) {
        if(bp[i].generation!=generation)return FALSE;
        if(bp[i].api!=api)return FALSE; /* entry/return collision unsupported */
        if(!api&&!bp[i].enabled) {
            if(!owner601(address)||!bytewrite(address,0xcc))return FALSE;
            bp[i].enabled=TRUE;bp[i].armed=TRUE;
        }
        *index=i;return TRUE;
    }
    if(bp_count==256||!readmem(address,&original,1)||original==0xcc)return FALSE;
    i=bp_count++;bp[i].address=address;bp[i].original=original;bp[i].api=api;
    bp[i].generation=generation;
    if(!bytewrite(address,0xcc))return FALSE;
    bp[i].armed=TRUE;bp[i].enabled=TRUE;*index=i;
    wsprintfA(msg,"BP %08lx %08lx %08lx %08lx\r\n",i,address,api,owner);line(msg);
    event("BPOWNER",i,generation,0);event("BPCODE",i,generation,original);return !failed;
}
static BOOL arm(void) {
    DWORD i,index,address,iat[2]={IAT_LOAD601,IAT_PROC601};
    for(i=0;i<2;i++) {
        if(!readmem(iat[i],&address,4)||!addbp(address,i+1,&index)||index!=i)return FALSE;
        event("ARM",i,iat[i],address);
    }return TRUE;
}
static BOOL request(DWORD which,DWORD tid,CONTEXT *ctx) {
    DWORD stack[3],name,i;char hex[513],s[680];BYTE c;const char digits[]="0123456789abcdef";
    if(!readmem(ctx->Esp,stack,which?12:8))return FALSE;
    name=stack[which?2:1];
    if(which&&name<=65535) {wsprintfA(s,"ORD %08lx %08lx %08lx %08lx\r\n",tid,stack[0],stack[1],name);line(s);return !failed;}
    for(i=0;i<256;i++) {
        if(name+i<name||!readmem(name+i,&c,1))return FALSE;
        if(!c)break;
        hex[i*2]=digits[c>>4];hex[i*2+1]=digits[c&15];
    }
    if(i==256)return FALSE;
    hex[i*2]=0;wsprintfA(s,"%s %08lx %08lx %08lx %s\r\n",which?"PROC":"LOAD",tid,stack[0],which?stack[1]:0,hex);line(s);return !failed;
}
static DWORD select601(DWORD module,DWORD name) {
    char text[256];BYTE c;DWORD i;
    if(name<=65535)return name==7&&module==probe_module&&resolved[14]?14:0;
    for(i=0;i<256;i++){if(name+i<name||!readmem(name+i,&c,1))return 0;text[i]=(char)c;if(!c)break;}
    if(i==256)return 0;
    if(!lstrcmpA(text,"BitBlt"))return 3;
    if(!lstrcmpA(text,"CreateDIBSection"))return 4;
    if(!lstrcmpA(text,"DirectDrawCreate"))return 5;
    if(!lstrcmpA(text,"StretchDIBits"))return 11;
    if(!lstrcmpA(text,"probe601"))return 14;
    if(!lstrcmpA(text,"probe_dib604"))return 15;
    if(!lstrcmpA(text,"probe_phase605"))return 16;
    return 0;
}
static BOOL words601(DWORD id,DWORD phase,DWORD address,DWORD n) {
    DWORD v[36],i;char s[64];
    if(n>36||address>0xffffffffu-n*4||!readmem(address,v,n*4))return FALSE;
    wsprintfA(s,"WORDS %08lx %08lx %08lx %08lx",id,phase,address,n);line(s);
    for(i=0;i<n;i++){wsprintfA(s," %08lx",v[i]);line(s);}line("\r\n");return !failed;
}
static BOOL interface601(DWORD id,DWORD object,BOOL surface) {
    DWORD vtable,entries[36],index,n=surface?36:23;char msg[160];
    if(!object||!readmem(object,&vtable,4)||!readmem(vtable,entries,n*4))return FALSE;
    wsprintfA(msg,"OBJECT %08lx %08lx %08lx %08lx\r\n",id,object,vtable,n);line(msg);
    if(!words601(id,2,vtable,n))return FALSE;
    if(surface)return addbp(entries[2],9,&index)&&addbp(entries[22],10,&index)&&addbp(entries[5],13,&index);
    return addbp(entries[2],6,&index)&&addbp(entries[20],7,&index)&&addbp(entries[6],8,&index);
}
static BOOL outputs601(FRAME601 *f,DWORD value) {
    DWORD pointer=0,index,address=0;char s[160];
    if(f->api==2&&f->selected&&value) {
        if(resolved[f->selected]&&resolved[f->selected]!=value)return FALSE;
        if(!addbp(value,f->selected,&index))return FALSE;
        resolved[f->selected]=value;
        if(f->selected==14)probe_module=f->arg0;
    }
    if(f->api==4)address=f->args[3];
    if(f->api==5)address=f->args[1];
    if(f->api==8)address=f->args[2];
    if(f->api==4||f->api==5||f->api==8) {
        if(f->api==4&&!address){event("OUTPUT_ABSENT",f->id,f->api,0);return !failed;}
        if(!address||!readmem(address,&pointer,4))return FALSE;
        wsprintfA(s,"OUTPUT %08lx %08lx %08lx %08lx\r\n",f->id,f->api,address,pointer);line(s);
        if(f->api==4&&value&&!pointer)return FALSE;
        if((f->api==5||f->api==8)&&!(value&0x80000000u)) {
            if(!interface601(f->id,pointer,f->api==8))return FALSE;
        }
    }
    if(f->api==10&&!(value&0x80000000u)&&!words601(f->id,1,f->args[1],27))return FALSE;
    return !failed;
}
static BOOL observe(DWORD index,THREAD *t,CONTEXT *c) {
    DWORD stack[14],retindex,cleanup,i;FRAME601 f;int paired;char s[220];
    if(bp[index].api) {
        if(bp[index].api==11&&!hit617(&timing,phase_state.phase,GetTickCount()))return FALSE;
        if(bp[index].api>=3&&seen[bp[index].api]>=32) {
            if(bp[index].api==11){
                if(!phase_caps[phase_state.phase]){event("CAP",11,seen[11],bp[index].address);phase_caps[phase_state.phase]=1;}
                phase_skipped[phase_state.phase]++;return TRUE;
            }
            bp[index].enabled=FALSE;event("CAP",bp[index].api,seen[bp[index].api],bp[index].address);return TRUE;
        }
        if(++requests>4096||!readmem(c->Esp,stack,(nargs[bp[index].api]+1)*4))return FALSE;
        zero(&f,sizeof(f));f.id=requests;f.api=bp[index].api;f.ret=stack[0];
        f.entry_sp=c->Esp;f.arg0=nargs[f.api]?stack[1]:0;f.arg1=nargs[f.api]>1?stack[2]:0;
        for(i=0;i<nargs[f.api];i++)f.args[i]=stack[i+1];
        if(f.api==2)f.selected=select601(f.arg0,f.arg1);
        cleanup=(f.api==14||f.api==15||f.api==16)?0:nargs[f.api]*4;
        if(!enter601(&t->stack,f,cleanup)||!addbp(f.ret,0,&retindex))return FALSE;
        bp[retindex].refs++;seen[f.api]++;
        if(f.api==11&&!stamp617(&timing,0,f.id,phase_state.phase,GetTickCount()))return FALSE;
        if(f.api<3&&!request(f.api-1,t->id,c))return FALSE;
        wsprintfA(s,"CALL %08lx %08lx %08lx %08lx %08lx %08lx %08lx %08lx\r\n",
            f.id,t->id,f.api,f.ret,f.entry_sp,f.arg0,f.arg1,bp[index].address);line(s);
        wsprintfA(s,"ARGS %08lx %08lx",f.id,nargs[f.api]);line(s);
        for(i=0;i<nargs[f.api];i++){wsprintfA(s," %08lx",f.args[i]);line(s);}line("\r\n");
        if(f.api==8&&!words601(f.id,0,f.args[1],27))return FALSE;
        if((f.api==4||f.api==11||f.api==15)&&!dibobserve604(f.id,f.args[f.api==4?1:f.api==11?10:0]))return FALSE;
    }else {
        paired=leave601(&t->stack,bp[index].address,c->Esp,&f);
        if(paired<0)return FALSE;
        if(!paired) {event("STALE",t->id,bp[index].address,c->Esp);return TRUE;}
        if(!bp[index].refs)return FALSE;
        if(--bp[index].refs==0)bp[index].enabled=FALSE;
        returns++;
        if(f.api==11&&!stamp617(&timing,1,f.id,phase_state.phase,GetTickCount()))return FALSE;
        wsprintfA(s,"RETURN %08lx %08lx %08lx %08lx %08lx %08lx\r\n",
            f.id,t->id,f.api,bp[index].address,c->Esp,c->Eax);line(s);
        if(!outputs601(&f,c->Eax))return FALSE;
    }
    return !failed;
}
static BOOL ownedbreak(DEBUG_EVENT *e,DWORD index) {
    CONTEXT c;THREAD *t=thread(e->dwThreadId);
    if(!t||step_id||!bp[index].armed)return FALSE;
    zero(&c,sizeof(c));c.ContextFlags=CONTEXT_CONTROL|CONTEXT_INTEGER;
    if(!GetThreadContext(t->h,&c)||c.Eip!=bp[index].address+1||(c.EFlags&0x100))return FALSE;
    if(!phasecheck605()||!observe(index,t,&c)||!holdothers(t->id)||!bytewrite(bp[index].address,bp[index].original))return FALSE;
    bp[index].armed=FALSE;c.Eip--;c.EFlags|=0x100;
    if(!SetThreadContext(t->h,&c))return FALSE;
    step_id=t->id;step_bp=index;return TRUE;
}
static BOOL stepped(DEBUG_EVENT *e) {
    THREAD *t=thread(e->dwThreadId);CONTEXT c;
    if(!t||e->dwThreadId!=step_id)return FALSE;
    zero(&c,sizeof(c));c.ContextFlags=CONTEXT_CONTROL;
    if(!GetThreadContext(t->h,&c))return FALSE;
    c.EFlags&=~0x100;
    if(!SetThreadContext(t->h,&c))return FALSE;
    if(bp[step_bp].enabled) {
        if(!bytewrite(bp[step_bp].address,0xcc))return FALSE;
        bp[step_bp].armed=TRUE;
    }step_id=0;return releaseothers();
}
void WINAPI mainCRTStartup(void) {
    STARTUPINFOA si;PROCESS_INFORMATION pi;DEBUG_EVENT e;DWORD status,count=0,i,j,exitcode=99,killat=0;char cmd[]="subject617 1";HANDLE pf;DWORD id[4],written;FILETIME ct,et,kt,ut;
    logfile=CreateFileA("C:\\xwn617\\trace.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,0,0);
    if(logfile==INVALID_HANDLE_VALUE)ExitProcess(90);
    SetLastError(0);phase_request=CreateEventA(0,TRUE,FALSE,"XWN617PhaseRequest");
    if(!phase_request||GetLastError()==ERROR_ALREADY_EXISTS){event("EVENT_FAIL",1,0,0);ExitProcess(92);}
    SetLastError(0);phase_ack=CreateEventA(0,TRUE,FALSE,"XWN617PhaseAck");
    if(!phase_ack||GetLastError()==ERROR_ALREADY_EXISTS){event("EVENT_FAIL",2,0,0);ExitProcess(93);}
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
    if(!CreateProcessA("C:\\xwn617-kit\\subject.exe",cmd,0,0,FALSE,DEBUG_ONLY_THIS_PROCESS,0,"C:\\xwn617-kit",&si,&pi)) {event("CREATE_FAIL",GetLastError(),0,0);CloseHandle(logfile);ExitProcess(91);}
    process=pi.hProcess;CloseHandle(pi.hThread);started=GetTickCount();
    zero(&ct,sizeof(ct));id[0]=pi.dwProcessId;id[1]=GetCurrentProcessId();
    if(!GetProcessTimes(process,&ct,&et,&kt,&ut))failed=TRUE;
    id[2]=ct.dwLowDateTime;id[3]=ct.dwHighDateTime;
    pf=CreateFileA("C:\\xwn617\\identity.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(pf==INVALID_HANDLE_VALUE)failed=TRUE;
    else {if(!WriteFile(pf,id,sizeof(id),&written,0)||written!=sizeof(id)||!FlushFileBuffers(pf))failed=TRUE;CloseHandle(pf);}
    event("COST_PID",id[0],id[1],0);event("COST_CREATED",id[2],id[3],0);
    while(!exited) {
        if(GetTickCount()-started>60000||count>10000)failed=TRUE;
        if(failed&&!killat) {event("TERMINATE",GetLastError(),requests,step_id);TerminateProcess(process,97);killat=GetTickCount();}
        if(killat&&GetTickCount()-killat>5000)break;
        if(!WaitForDebugEvent(&e,100)) {if(GetLastError()!=ERROR_SEM_TIMEOUT)failed=TRUE;continue;}
        count++;status=DBG_CONTINUE;
        switch(e.dwDebugEventCode) {
        case CREATE_PROCESS_DEBUG_EVENT:
            if(e.dwProcessId!=pi.dwProcessId||!addthread(e.dwThreadId,e.u.CreateProcessInfo.hThread))failed=TRUE;
            if(e.u.CreateProcessInfo.hFile)CloseHandle(e.u.CreateProcessInfo.hFile);
            event("IMAGE",(DWORD)e.u.CreateProcessInfo.lpBaseOfImage,e.dwThreadId,0);
            if(!module601((DWORD)e.u.CreateProcessInfo.lpBaseOfImage))failed=TRUE;
            break;
        case CREATE_THREAD_DEBUG_EVENT:
            if(!addthread(e.dwThreadId,e.u.CreateThread.hThread))failed=TRUE;
            event("THREAD",e.dwThreadId,0,0);break;
        case EXIT_THREAD_DEBUG_EVENT: {
            THREAD *t=thread(e.dwThreadId);if(!t||t->held||t->stack.depth||step_id==e.dwThreadId)failed=TRUE;
            if(t){t->id=0;t->h=0;}break;
        }
        case LOAD_DLL_DEBUG_EVENT:
            event("DLL",(DWORD)e.u.LoadDll.lpBaseOfDll,0,0);
            if(!module601((DWORD)e.u.LoadDll.lpBaseOfDll))failed=TRUE;
            if(e.u.LoadDll.hFile)CloseHandle(e.u.LoadDll.hFile);
            break;
        case EXCEPTION_DEBUG_EVENT:
            status=DBG_EXCEPTION_NOT_HANDLED;
            if(!failed&&e.u.Exception.ExceptionRecord.ExceptionCode==EXCEPTION_BREAKPOINT) {
                if(!initial) {initial=TRUE;if(!arm())failed=TRUE;status=DBG_CONTINUE;}
                else for(i=0;i<bp_count;i++)if(!bp[i].retired&&(DWORD)e.u.Exception.ExceptionRecord.ExceptionAddress==bp[i].address) {if(!ownedbreak(&e,i))failed=TRUE;status=DBG_CONTINUE;break;}
            }else if(!failed&&e.u.Exception.ExceptionRecord.ExceptionCode==EXCEPTION_SINGLE_STEP&&step_id) {
                if(!stepped(&e))failed=TRUE;
                status=DBG_CONTINUE;
            }
            if(status==DBG_EXCEPTION_NOT_HANDLED)event("EXCEPTION",e.u.Exception.ExceptionRecord.ExceptionCode,e.u.Exception.dwFirstChance,e.dwThreadId);
            break;
        case UNLOAD_DLL_DEBUG_EVENT:
            if(!unload601((DWORD)e.u.UnloadDll.lpBaseOfDll))failed=TRUE;
            break;
        case EXIT_PROCESS_DEBUG_EVENT:
            exitcode=e.u.ExitProcess.dwExitCode;exited=TRUE;
            for(i=0;i<64;i++)if(threads[i].stack.depth)failed=TRUE;
            if(step_id||returns!=requests)failed=TRUE;
            break;
        case RIP_EVENT:failed=TRUE;break;
        default:break;
        }
        if(!ContinueDebugEvent(e.dwProcessId,e.dwThreadId,status))failed=TRUE;
    }
    event("PHASE_END",phase_state.phase,phase_skipped[0],phase_skipped[1]);
    for(i=0;i<2;i++){
        event("COST_HIT_START",i,timing.first[i],timing.hits[i]);
        event("COST_HIT_END",i,timing.last[i],timing.hits[i]);
        for(j=0;j<timing.hits[i];j++)event("COST_HIT",i,j,timing.hit_ticks[i][j]);
    }
    for(i=0;i<timing.count;i++)event(timing.rows[i].kind?"COST_RETURN":"COST_CALL",timing.rows[i].id,timing.rows[i].phase,timing.rows[i].tick);
    event("TOTAL",requests,returns,bp_count);
    event("END",exitcode,requests,failed?1:0);
    FlushFileBuffers(logfile);CloseHandle(logfile);CloseHandle(process);CloseHandle(phase_request);CloseHandle(phase_ack);
    ExitProcess(!failed&&exited&&initial&&requests&&exitcode==0?0:1);
}
