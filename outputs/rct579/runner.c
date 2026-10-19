/* SPDX-License-Identifier: MIT. NT5 owned Welcome inventory/normal-close control. */
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
static HANDLE logh; static char wanted[100]; static HWND candidate; static DWORD count;
static void zero(void*p,DWORD n){BYTE*b=p;while(n--)*b++=0;}
static void text(const char*s){DWORD n=0;WriteFile(logh,s,lstrlenA(s),&n,0);FlushFileBuffers(logh);}
static void number(const char*k,DWORD v){char s[160];wsprintfA(s,"%s=%lu\r\n",k,v);text(s);}
static BOOL pathof(DWORD pid,char*p){HANDLE h;MODULEENTRY32 m;BOOL ok;h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid);if(h==INVALID_HANDLE_VALUE)return FALSE;zero(&m,sizeof(m));m.dwSize=sizeof(m);ok=Module32First(h,&m);if(ok)lstrcpynA(p,m.szExePath,MAX_PATH);CloseHandle(h);return ok;}
static BOOL identity(HWND w,BOOL logit){DWORD pid=0;char t[200],c[100],p[MAX_PATH],expected[MAX_PATH],s[1000];RECT r;BOOL known,match;
 zero(t,sizeof(t));zero(c,sizeof(c));zero(p,sizeof(p));zero(&r,sizeof(r));GetWindowThreadProcessId(w,&pid);GetWindowTextA(w,t,sizeof(t));GetClassNameA(w,c,sizeof(c));GetWindowRect(w,&r);known=pathof(pid,p);
 GetSystemDirectoryA(expected,MAX_PATH-20);lstrcatA(expected,"\\welcome.exe");
 match=IsWindowVisible(w)&&known&&!lstrcmpiA(p,expected)&&!lstrcmpA(t,"Getting Started")&&wanted[0]&&!lstrcmpA(c,wanted);
 if(logit){wsprintfA(s,"window hwnd=%08lx pid=%lu visible=%lu module_known=%lu rect=%ld,%ld,%ld,%ld class=[%s] title=[%s] module=[%s] candidate=%lu\r\n",(DWORD)w,pid,(DWORD)IsWindowVisible(w),(DWORD)known,r.left,r.top,r.right,r.bottom,c,t,p,(DWORD)match);text(s);}return match;
}
static BOOL CALLBACK enumerate(HWND w,LPARAM unused){(void)unused;if(IsWindowVisible(w)&&identity(w,TRUE)){candidate=w;count++;}return TRUE;}
static BOOL CALLBACK child(HWND w,LPARAM unused){char c[100],t[200],s[400];DWORD_PTR check=0; (void)unused;GetClassNameA(w,c,sizeof(c));GetWindowTextA(w,t,sizeof(t));if(!lstrcmpA(c,"Button"))SendMessageTimeoutA(w,BM_GETCHECK,0,0,SMTO_ABORTIFHUNG,1000,&check);wsprintfA(s,"child id=%d class=[%s] title=[%s] visible=%lu check=%lu\r\n",GetDlgCtrlID(w),c,t,(DWORD)IsWindowVisible(w),(DWORD)check);text(s);return TRUE;}
static void restart(void){HANDLE token;TOKEN_PRIVILEGES tp;BOOL ok=FALSE;if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){SetLastError(0);ok=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;}CloseHandle(token);}number("restart_privilege",ok);number("restart_requested",ok&&ExitWindowsEx(EWX_REBOOT,0));}
void WINAPI mainCRTStartup(void){char*arg=GetCommandLineA();BOOL closeit=FALSE,ok=FALSE;DWORD pid=0,wait=WAIT_FAILED;HANDLE process=0;HWND fake=0;WNDCLASSA wc;
 if(*arg=='"'){arg++;while(*arg&&*arg!='"')arg++;if(*arg)arg++;}else while(*arg&&*arg!=' ')arg++;
 while(*arg==' ')arg++;
 if(lstrlenA(arg)>=7&&arg[0]=='/'&&arg[1]=='c'&&arg[2]=='l'&&arg[3]=='o'&&arg[4]=='s'&&arg[5]=='e'&&arg[6]=='='){lstrcpynA(wanted,arg+7,sizeof(wanted));closeit=TRUE;}
 CreateDirectoryA("C:\\xwn579",0);
 logh=CreateFileA(closeit?"C:\\xwn579\\close.txt":"C:\\xwn579\\inventory.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(logh==INVALID_HANDLE_VALUE)ExitProcess(90);
 number("schema",579);number("close_mode",closeit);number("tick_start",GetTickCount());
 if(closeit){zero(&wc,sizeof(wc));wc.lpfnWndProc=DefWindowProcA;wc.hInstance=GetModuleHandleA(0);wc.lpszClassName=wanted;number("fake_class_registered",RegisterClassA(&wc));fake=CreateWindowA(wanted,"Getting Started",WS_OVERLAPPEDWINDOW|WS_VISIBLE,0,0,120,80,0,0,wc.hInstance,0);number("fake_created",fake!=0);}
 EnumWindows(enumerate,0);number("candidate_count",count);
 if(closeit&&count==1&&fake&&identity(candidate,TRUE)){EnumChildWindows(candidate,child,0);GetWindowThreadProcessId(candidate,&pid);process=OpenProcess(SYNCHRONIZE|PROCESS_QUERY_INFORMATION,FALSE,pid);number("process_open",process!=0);
 if(process&&identity(candidate,TRUE)){number("close_posted",PostMessageA(candidate,WM_CLOSE,0,0));wait=WaitForSingleObject(process,10000);number("process_wait",wait);number("window_gone",!IsWindow(candidate));number("fake_survived",IsWindow(fake));ok=!IsWindow(candidate)&&IsWindow(fake);}
 if(process)CloseHandle(process);}
 if(fake){DestroyWindow(fake);}number("close_qualified",ok);number("tick_end",GetTickCount());if(closeit)restart();CloseHandle(logh);ExitProcess(closeit&&!ok?1:0);
}
