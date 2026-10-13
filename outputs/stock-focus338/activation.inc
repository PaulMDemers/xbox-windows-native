#include "activation.h"
#ifndef XWN_EMULATOR_ACTIVATION313
#define XWN_EMULATOR_ACTIVATION313 0
#endif
static struct x313_budget ActivationBudget;
static DWORD ActivationLastState;
static struct x313_gui read_gui313(DWORD tid) {
    GUITHREADINFO g={0};struct x313_gui r={0};g.cbSize=sizeof(g);
    r.ok=GetGUIThreadInfo(tid,&g)?1:0;r.active=(DWORD)g.hwndActive;r.flags=g.flags;
    r.capture=(DWORD)g.hwndCapture;r.menu=(DWORD)g.hwndMenuOwner;r.move=(DWORD)g.hwndMoveSize;return r;
}
static BOOL activation_state313(HWND h,struct x313_state *s) {
    struct xwn_window201 w;FILETIME stamp;DWORD fgpid=0;
    if(PendingWindow||WaitForSingleObject(CurrentProcess,0)!=WAIT_TIMEOUT||
       !creation(CurrentProcess,&stamp)||!same(stamp,CurrentCreation)||
       !getcommand(CurrentProcess,Command)||!xwn_equal(Command,OriginalCommand)||
       !xwn_target(Command,Emulator)||!inspect(h,&w)||!xwn_eligible(&w,CurrentPid)||!welcome(h))return FALSE;
    s->enabled=XWN_EMULATOR_ACTIVATION313;s->mode=Mode;s->emulator=Emulator;
    s->pid=CurrentPid;s->lo=stamp.dwLowDateTime;s->hi=stamp.dwHighDateTime;s->hwnd=(DWORD)h;s->tid=w.tid;
    s->fg=(DWORD)GetForegroundWindow();s->fgtid=GetWindowThreadProcessId((HWND)s->fg,&fgpid);s->fgpid=fgpid;
    s->target=read_gui313(s->tid);s->foreground=read_gui313(s->fgtid);
    return x313_admit(s)&&GetForegroundWindow()==(HWND)s->fg;
}
static void activate313(HWND h,DWORD tid) {
    struct x313_state before={0},after={0};DWORD result;
    if(!XWN_EMULATOR_ACTIVATION313||!Mode||!Emulator||GetForegroundWindow()==h)return;
    if(GetTickCount()-ActivationLastState>=5000||!ActivationLastState){
        ActivationLastState=GetTickCount();gui_state("ACTIVATE_WAIT313",tid);
    }
    if(!activation_state313(h,&before)||!x313_reserve(&ActivationBudget,&before))return;
    record("ACTIVATE_OWNER313",before.pid,before.lo,before.hi);
    record("ACTIVATE_INTENT313",before.pid,before.hwnd,ActivationBudget.count);
    gui_state("ACTIVATE_BEFORE313",tid);
    /* Durable logging yields. Revalidate both actual GUI owners and the original process. */
    if(!activation_state313(h,&after)||!x313_same(&before,&after)){
        record("FAIL_ACTIVATE_STALE313",CurrentPid,(DWORD)h,0);ExitProcess(103);
    }
    result=SetForegroundWindow(h)?1:0;
    record("ACTIVATE_RESULT313",CurrentPid,(DWORD)h,result);gui_state("ACTIVATE_AFTER313",tid);
    /* Return to the unchanged original foreground/active/identity Cancel checks. */
}
