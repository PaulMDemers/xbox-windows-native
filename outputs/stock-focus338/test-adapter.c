/* Exact activation adapter, modeled Win32/process/log calls. No live GUI claim. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#define XWN_EMULATOR_ACTIVATION313 1
#define TRUE 1
#define FALSE 0
#define WAIT_TIMEOUT 258
typedef uint32_t DWORD;
typedef uint32_t HWND;
typedef int BOOL;
typedef struct {DWORD dwLowDateTime,dwHighDateTime;} FILETIME;
typedef struct {DWORD cbSize,flags;HWND hwndActive,hwndFocus,hwndCapture,hwndMenuOwner,hwndMoveSize;} GUITHREADINFO;
struct xwn_window201 {DWORD tid;};
static DWORD Mode=1,Emulator=1,CurrentPid=10,CurrentProcess=10;
static HWND PendingWindow;
static FILETIME CurrentCreation={100,1};
static char Command[512],OriginalCommand[512]="known";
static DWORD foreground=30,flags,capture,menu,move,alive=1,known=1,eligible=1,page=1,gui=1,identity=1;
static DWORD inactive,alien,transition;
static DWORD calls,deny,stale,checks,ticks=10,exits;
static jmp_buf trap;
static void check(int p){checks++;if(!p){fprintf(stderr,"check %u failed\n",checks);exit(1);}}
static DWORD GetTickCount(void){return ticks;}
static HWND GetForegroundWindow(void){return foreground;}
static DWORD GetWindowThreadProcessId(HWND h,DWORD *p){*p=h==20?10:30;return h==20?11:31;}
static BOOL GetGUIThreadInfo(DWORD t,GUITHREADINFO *g){g->hwndActive=t==11?(alien?40:(inactive?0:20)):30;g->flags=flags;g->hwndCapture=capture;g->hwndMenuOwner=menu;g->hwndMoveSize=move;return gui;}
static DWORD WaitForSingleObject(DWORD h,DWORD ms){(void)h;(void)ms;return alive?WAIT_TIMEOUT:0;}
static BOOL creation(DWORD h,FILETIME *f){(void)h;*f=CurrentCreation;if(!identity)f->dwLowDateTime++;return 1;}
static BOOL same(FILETIME a,FILETIME b){return a.dwLowDateTime==b.dwLowDateTime&&a.dwHighDateTime==b.dwHighDateTime;}
static BOOL getcommand(DWORD h,char *b){(void)h;strcpy(b,known?"known":"unknown");return 1;}
static BOOL xwn_equal(const char *a,const char *b){return !strcmp(a,b);}
static DWORD xwn_target(const char *b,DWORD emu){(void)emu;return !strcmp(b,"known");}
static BOOL inspect(HWND h,struct xwn_window201 *w){w->tid=11;return h==20;}
static BOOL xwn_eligible(struct xwn_window201 *w,DWORD p){(void)w;return p==10&&eligible;}
static BOOL welcome(HWND h){return h==20&&page;}
static void record(const char *l,DWORD a,DWORD b,DWORD c){(void)a;(void)b;(void)c;if(stale&&!strcmp(l,"ACTIVATE_INTENT313"))identity=0;if(transition&&!strcmp(l,"ACTIVATE_INTENT313"))inactive=!inactive;}
static void gui_state(const char *s,DWORD tid){(void)s;(void)tid;}
static void ExitProcess(DWORD e){exits=e;longjmp(trap,1);}
static BOOL SetForegroundWindow(HWND h){calls++;if(!deny){foreground=h;inactive=0;}return !deny;}
#include "activation.inc"
static void reset(void){memset(&ActivationBudget,0,sizeof(ActivationBudget));ActivationLastState=0;inactive=alien=transition=0;foreground=30;flags=capture=menu=move=deny=stale=calls=exits=PendingWindow=0;alive=known=eligible=page=gui=identity=Mode=Emulator=1;CurrentCreation.dwLowDateTime=100;}
int main(void){
    struct x313_state a,b;struct x313_budget budget;uint32_t n,i;
    reset();check(activation_state313(20,&a));
    for(n=0;n<32;n++){b=a;b.target.flags=1u<<n;check(x313_admit(&b)==(n==0));b=a;b.foreground.flags=1u<<n;check(x313_admit(&b)==(n==0));}
    for(n=0;n<12;n++){reset();switch(n){case 0:Mode=0;break;case 1:Emulator=0;break;case 2:alive=0;break;case 3:known=0;break;case 4:eligible=0;break;case 5:page=0;break;case 6:gui=0;break;case 7:identity=0;break;case 8:capture=1;break;case 9:menu=1;break;case 10:move=1;break;case 11:PendingWindow=20;break;}activate313(20,11);check(calls==0&&ActivationBudget.count==0);}
    reset();activate313(20,11);check(calls==1&&foreground==20&&ActivationBudget.count==1);activate313(20,11);check(calls==1);
    reset();deny=1;for(i=0;i<10000;i++)activate313(20,11);check(calls==1&&foreground==30&&ActivationBudget.count==1);
    reset();stale=1;if(!setjmp(trap))activate313(20,11);check(exits==103&&calls==0&&ActivationBudget.count==1);
    reset();check(activation_state313(20,&a));memset(&budget,0,sizeof(budget));
    for(i=0;i<8;i++){a.lo=100+i;check(x313_reserve(&budget,&a));check(!x313_reserve(&budget,&a));}
    a.lo=108;check(!x313_reserve(&budget,&a)&&budget.count==8);
    for(i=0;i<11;i++){b=a;switch(i){case 0:b.pid++;break;case 1:b.lo++;break;case 2:b.hi++;break;case 3:b.hwnd++;break;case 4:b.tid++;break;case 5:b.fg++;break;case 6:b.fgpid++;break;case 7:b.fgtid++;break;case 8:b.target.capture=1;break;case 9:b.foreground.menu=1;break;case 10:b.target.ok=0;break;}check(!x313_same(&a,&b));}
    reset();inactive=1;activate313(20,11);check(calls==1&&foreground==20&&!inactive&&ActivationBudget.count==1);
    reset();alien=1;activate313(20,11);check(calls==0&&ActivationBudget.count==0);
    reset();inactive=deny=1;for(i=0;i<10000;i++)activate313(20,11);check(calls==1&&inactive&&ActivationBudget.count==1);
    reset();inactive=transition=1;if(!setjmp(trap))activate313(20,11);check(exits==103&&calls==0&&ActivationBudget.count==1);
    reset();inactive=1;Mode=0;activate313(20,11);check(calls==0);
    reset();inactive=1;Emulator=0;activate313(20,11);check(calls==0);
    check(x313_same(&a,&a));printf("PASS %u assertions; denied activation attempted once across10000 polls; stale identity exits before API\n",checks);return 0;
}
